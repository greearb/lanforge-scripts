//
// LANforge-GUI Source Code
// Copyright (C) 1999-2018  Candela Technologies Inc
// http://www.candelatech.com
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU Library General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
//
// Contact:  Candela Technologies <support@candelatech.com> if you have any
//           questions.
//

import java.util.concurrent.*;
import java.io.*;
import java.net.URL;
import java.util.*;
import java.nio.file.*;

public class kpi {
   String lc_osname;
   String home_dir;
   static final String out_sep = "\t";
   static final String in_sep = "\t";
   
   public static int TEST_ID_IDX = 7;
   public static int SHORT_DESC_IDX = 8;
   public static int NUMERIC_SCORE_IDX = 10;

   public static String AP_AUTO_BASIC_CX = "ap_auto_basic_cx";

   public kpi() {
      priv_init();
   }

   public boolean is_mac() {
      return lc_osname.startsWith("mac os x");
   }
   public boolean is_win() {
      return lc_osname.startsWith("windows");
   }
   public boolean is_linux() {
      return lc_osname.startsWith("linux");
   }

   private void priv_init() {
      lc_osname = System.getProperty("os.name").toLowerCase();
      home_dir = System.getProperty("user.home");
   }

   public static void main(String[] args) {
      kpi k = new kpi();
      k.work(args);
   }

   public void work(String[] args) {
      String dir = null;

      for (int i = 0; i<args.length; i++) {
         if (args[i].equals("--dir")) {
            dir = args[i+1];
         }
         else if (args[i].equals("--help") || args[i].equals("-h") || args[i].equals("-?")) {
            System.out.println("Usage: $0 --dir /path/to/test-collection");
            System.exit(0);
         }
      }

      Hashtable<String, String> test_names = new Hashtable();
      Vector<Run> runs = new Vector();

      try {
         DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get(dir));
         for (Path file: stream) {
            File f = file.toFile(); // this is the test run dir
            //System.out.println("Checking sub-directory/file (run): " + f.getAbsolutePath());
            // Inside of it is individual tests.
            if (!f.isDirectory()) {
               continue;
            }
            DirectoryStream<Path> stream2 = Files.newDirectoryStream(file);
            Run run = null;

            for (Path file2: stream2) {
               File f2 = file2.toFile(); // this is the test case dir in the test run
               // Directory full of test results?
               if (f2.isDirectory()) {
                  File kf = new File(f2.getAbsolutePath() + File.separator + "kpi.csv");
                  try {
                     BufferedReader br = new BufferedReader(new FileReader(kf));
                     test_names.put(f2.getName(), f2.getName());
                     if (run == null) {
                        run = new Run(f.getName());
                        runs.add(run);
                     }
                     Test test = new Test(f2.getName());
                     run.addTest(test);
                     String line;
                     while ((line = br.readLine()) != null) {
                        test.addLine(line);
                     }
                  }
                  catch (FileNotFoundException enf) {
                     // ignore
                  }
                  catch (Exception e) {
                     e.printStackTrace();
                  }
               }
            }
         }
      } catch (IOException | DirectoryIteratorException x) {
         // IOException can never be thrown by the iteration.
         // In this snippet, it can only be thrown by newDirectoryStream.
         System.err.println(x);
      }

      // We have read everything into memory.
      // For each test, generate data over time.
      Hashtable<String, History> hist_data = new Hashtable();
      Vector v = new Vector(test_names.keySet());
      Collections.sort(v);
      Iterator it = v.iterator();
      while (it.hasNext()) {
         String tname = (String)it.next();
         // For each test, find all runs that have this test and consolidate data
         for (int i = 0; i<runs.size(); i++) {
            Run run = runs.elementAt(i);
            Test t = run.findTest(tname);
            if (t != null) {
               try {
                  History hist = hist_data.get(tname);
                  if (hist == null) {
                     hist = new History();
                     hist_data.put(tname, hist);
                  }
                  for (int z = 0; z<t.data.size(); z++) {
                     Row r = t.data.elementAt(z);
                     StringBuffer csv = hist.findCsv(r.getShortDescKey());
                     if (csv == null) {
                        csv = new StringBuffer();
                        hist.addCsv(csv, r.getShortDescKey(), r.getTestId() + ":  " + r.getShortDesc());
                     }
                     csv.append(i + kpi.out_sep + t.data.elementAt(z).getScore() + System.lineSeparator());
                  }
               }
               catch (Exception eee) {
                  eee.printStackTrace();
               }
            }
         }
      }

      // For all history, print out csv files
      v = new Vector(hist_data.keySet());
      for (Object hk : v) {
         History hist = hist_data.get(hk); // history per test
         Set<String> v2 = hist.csv.keySet();
         for (String ck: v2) {
            StringBuffer csv = hist.csv.get(ck);
            String title = hist.titles.get(ck);
            try {
               String cf = dir + File.separator + hk + "::" + ck + ".csv";
               FileWriter f = new FileWriter(cf);
               f.write(csv.toString());
               f.close();

               ShellExec exec = new ShellExec(true, true);
               int rv = exec.execute("gnuplot", null, true, "-e", "filename='" + cf + "'",
                                     "-e", "set title '" + title + "'",
                                     "default.plot");
               System.out.println("gnuplot for filename: " + cf + " rv: " + rv);
               System.out.println(exec.getOutput());
               System.out.println(exec.getError());

               File png = new File("plot.png");
               png.renameTo(new File(dir + File.separator + hk + "::" + ck + ".png"));
            }
            catch (Exception ee) {
               ee.printStackTrace();
            }
         }
      }

   } // ~work()
}

class History {
   Hashtable<String, StringBuffer> csv = new Hashtable();
   Hashtable<String, String> titles = new Hashtable();

   public History() {
   }

   StringBuffer findCsv(String n) {
      //System.out.println("findCsv, n: " + n);
      return csv.get(n);
   }

   void addCsv(StringBuffer b, String n, String title) {
      csv.put(n, b);
      titles.put(n, title);
   }
}

class Row {
   Vector<String> rdata = new Vector();
   String short_desc_key = null;

   String getScore() {
      return rdata.elementAt(kpi.NUMERIC_SCORE_IDX);
   }

   String getShortDesc() {
      return rdata.elementAt(kpi.SHORT_DESC_IDX);
   }

   String getTestId() {
      return rdata.elementAt(kpi.TEST_ID_IDX);
   }

   String getShortDescKey() {
      return short_desc_key;
   }

   void setShortDescKey(String s) {
      short_desc_key = s;
   }

   public String toString() {
      StringBuffer sb = new StringBuffer();
      sb.append("Row " + getShortDescKey() + "  ");
      for (int i = 0; i<rdata.size(); i++) {
         sb.append("[" + i + "] == " + rdata.elementAt(i) + "  ");
      }
      return sb.toString();
   }
}

class Test {
   String name;
   Vector<String> titles = null;
   Vector<Row> data = new Vector();
   Hashtable<String, String> descs = new Hashtable();

   public String test_rig;
   public String dut_hw_version;
   public String dut_sw_version;
   public String dut_model_num;
   public String dut_serial_num;

   public Test(String n) {
      name = n;
   }

   String getName() {
      return name;
   }

   void addLine(String l) {
      if (titles == null) {
         titles = new Vector();
         StringTokenizer st = new StringTokenizer(l, kpi.in_sep, true);
         boolean last_was_sep = false;
         while (st.hasMoreTokens()) {
            String tok = st.nextToken();
            if (tok.equals(kpi.in_sep)) {
               if (last_was_sep) {
                  titles.add(new String());
               }
               last_was_sep = true;
            }
            else {
               titles.add(tok);
               last_was_sep = false;
            }
         }
      }
      else {
         Row row = new Row();
         data.add(row);
         StringTokenizer st = new StringTokenizer(l, kpi.in_sep, true);
         int idx = 0;
         System.out.println("new line: " + l);
         boolean last_was_sep = false;
         while (st.hasMoreTokens()) {
            String rtok = st.nextToken();
            if (rtok.equals(kpi.in_sep)) {
               if (last_was_sep) {
                  row.rdata.add(new String());
                  idx++;
               }
               last_was_sep = true;
            }
            else {
               row.rdata.add(rtok);
               idx++;
               last_was_sep = false;
            }

            if (data.size() == 1) { // first row is being added
               if (titles.elementAt(idx - 1).equalsIgnoreCase("test-rig")) {
                  test_rig = rtok;
               }
               else if (titles.elementAt(idx - 1).equalsIgnoreCase("dut-hw-version")) {
                  dut_hw_version = rtok;
               }
               else if (titles.elementAt(idx - 1).equalsIgnoreCase("dut-sw-version")) {
                  dut_sw_version = rtok;
               }
               else if (titles.elementAt(idx - 1).equalsIgnoreCase("dut-model-num")) {
                  dut_model_num = rtok;
               }
            }
            //System.out.println("idx: " + idx);
         }
         //System.out.println("done tok reading loop");

         row.setShortDescKey(row.getShortDesc().replace(" ", "_"));
         //System.out.println("Row: " + row);
         descs.put(row.getShortDesc(), row.getShortDesc());
      }
   }
}

class Run {
   String name;
   Hashtable<String, Test> tests = new Hashtable();

   public Run(String n) {
      name = n;
   }

   String getName() {
      return name;
   }

   void addTest(Test t) {
      tests.put(t.getName(), t);
   }

   Test findTest(String n) {
      return tests.get(n);
   }
}


// From: https://stackoverflow.com/questions/882772/capturing-stdout-when-calling-runtime-exec

/**
 * Execute external process and optionally read output buffer.
 */
class ShellExec {
   private int exitCode;
   private boolean readOutput, readError;
   private StreamGobbler errorGobbler, outputGobbler;

   public ShellExec() { 
      this(false, false);
   }

   public ShellExec(boolean readOutput, boolean readError) {
      this.readOutput = readOutput;
      this.readError = readError;
   }

   /**
    * Execute a command.
    * @param command   command ("c:/some/folder/script.bat" or "some/folder/script.sh")
    * @param workdir   working directory or NULL to use command folder
    * @param wait  wait for process to end
    * @param args  0..n command line arguments
    * @return  process exit code
    */
   public int execute(String command, String workdir, boolean wait, String...args) throws IOException {
      String[] cmdArr;
      if (args != null && args.length > 0) {
         cmdArr = new String[1+args.length];
         cmdArr[0] = command;
         System.arraycopy(args, 0, cmdArr, 1, args.length);
      } else {
         cmdArr = new String[] { command };
      }

      ProcessBuilder pb =  new ProcessBuilder(cmdArr);
      File workingDir = (workdir==null ? new File(command).getParentFile() : new File(workdir) );
      pb.directory(workingDir);

      Process process = pb.start();

      // Consume streams, older jvm's had a memory leak if streams were not read,
      // some other jvm+OS combinations may block unless streams are consumed.
      errorGobbler  = new StreamGobbler(process.getErrorStream(), readError);
      outputGobbler = new StreamGobbler(process.getInputStream(), readOutput);
      errorGobbler.start();
      outputGobbler.start();

      exitCode = 0;
      if (wait) {
         try { 
            process.waitFor();
            exitCode = process.exitValue();                 
         } catch (InterruptedException ex) { }
      }
      return exitCode;
   }   

   public int getExitCode() {
      return exitCode;
   }

   public boolean isOutputCompleted() {
      return (outputGobbler != null ? outputGobbler.isCompleted() : false);
   }

   public boolean isErrorCompleted() {
      return (errorGobbler != null ? errorGobbler.isCompleted() : false);
   }

   public String getOutput() {
      return (outputGobbler != null ? outputGobbler.getOutput() : null);        
   }

   public String getError() {
      return (errorGobbler != null ? errorGobbler.getOutput() : null);        
   }

   //********************************************
   //********************************************    

    /**
     * StreamGobbler reads inputstream to "gobble" it.
     * This is used by Executor class when running 
     * a commandline applications. Gobblers must read/purge
     * INSTR and ERRSTR process streams.
     * http://www.javaworld.com/javaworld/jw-12-2000/jw-1229-traps.html?page=4
     */
   private class StreamGobbler extends Thread {
      private InputStream is;
      private StringBuilder output;
      private volatile boolean completed; // mark volatile to guarantee a thread safety

      public StreamGobbler(InputStream is, boolean readStream) {
         this.is = is;
         this.output = (readStream ? new StringBuilder(256) : null);
      }

      public void run() {
         completed = false;
         try {
            String NL = System.getProperty("line.separator", "\r\n");

            InputStreamReader isr = new InputStreamReader(is);
            BufferedReader br = new BufferedReader(isr);
            String line;
            while ( (line = br.readLine()) != null) {
               if (output != null)
                  output.append(line + NL); 
            }
         } catch (IOException ex) {
            // ex.printStackTrace();
         }
         completed = true;
      }

      /**
       * Get inputstream buffer or null if stream
       * was not consumed.
       * @return
       */
      public String getOutput() {
         return (output != null ? output.toString() : null);
      }

      /**
       * Is input stream completed.
       * @return
       */
      public boolean isCompleted() {
         return completed;
      }

   }

}
