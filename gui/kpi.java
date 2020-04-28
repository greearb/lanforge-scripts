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

import java.io.*;
import java.net.URL;
import java.util.*;
import java.nio.file.*;

public class kpi {
   String lc_osname;
   String home_dir;
   static final String out_sep = "\t";
   static final String in_sep = "\t";
   
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
                        hist.addCsv(csv, r.getShortDescKey());
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
            try {
               FileWriter f = new FileWriter(dir + File.separator + hk + "::" + ck + ".csv");
               f.write(csv.toString());
               f.close();
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

   public History() {
   }

   StringBuffer findCsv(String n) {
      //System.out.println("findCsv, n: " + n);
      return csv.get(n);
   }

   void addCsv(StringBuffer b, String n) {
      csv.put(n, b);
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
