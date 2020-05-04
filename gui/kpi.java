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

import java.text.*;
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
   
   public static int PRIORITY_IDX = 6;
   public static int TEST_ID_IDX = 7;
   public static int SHORT_DESC_IDX = 8;
   public static int NUMERIC_SCORE_IDX = 10;
   public static int NOTES_IDX = 11;
   public static int UNITS_IDX = 12;
   public static int GRAPH_GROUP_IDX = 13;

   public static String TESTBED_TEMPLATE = "testbed_template.html";
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
      try {
         k.work(args);
      }
      catch (Exception ee) {
         ee.printStackTrace();
      }
   }

   public static String toStringNum(double i, int precision) {
      NumberFormat nf = NumberFormat.getInstance();
      if (0.0 == i) {
         // Don't pad precision on '0', just adds needless clutter.
         return nf.format(i);
      }
      else {
         nf = (NumberFormat)(nf.clone());
         nf.setMaximumFractionDigits(precision);
         nf.setMinimumFractionDigits(precision);
         return nf.format(i);
      }
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
      Vector<String> test_namesv = new Vector();
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
                  DirectoryStream<Path> stream3 = Files.newDirectoryStream(file2);
                  Test test = new Test(f2.getName());
                  if (run == null) {
                     run = new Run(f.getName());
                     runs.add(run);
                  }
                  run.addTest(test);

                  for (Path file3: stream3) {
                     File f3 = file3.toFile();
                     String fname = f3.getName();
                     if (fname.equals("kpi.csv")) {
                        try {
                           BufferedReader br = new BufferedReader(new FileReader(f3));
                           if (test_names.get(f2.getName()) == null) {
                              test_names.put(f2.getName(), f2.getName());
                              test_namesv.add(f2.getName());
                           }
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
                     }// if kpi.csv
                     else if (fname.startsWith("kpi-") && fname.endsWith(".png")) {
                        test.addKpiImage(fname);
                     }
                  }// for all files in the test dir  
               }
            }
         }
      } catch (IOException | DirectoryIteratorException x) {
         // IOException can never be thrown by the iteration.
         // In this snippet, it can only be thrown by newDirectoryStream.
         System.err.println(x);
      }

      // Sort runs so that earliest is first.
      class SortbyDate implements Comparator<Run> { 
         // Used for sorting in ascending order of 
         // roll number 
         public int compare(Run a, Run b) { 
            long c = a.getDateMs() - b.getDateMs();
            if (c < 0)
               return -1;
            if (c > 0)
               return 1;
            return 0;
         }
      }

      runs.sort(new SortbyDate());

      // Link to latest test run that has the test id
      Hashtable<String, Run> test_id_links = new Hashtable();

      // We have read everything into memory.
      // For each test, generate data over time.
      Hashtable<String, History> hist_data = new Hashtable();
      Vector<History> hist_datav = new Vector();
      for (String tname: test_namesv) {
         // For each test, find all runs that have this test and consolidate data
         for (int i = 0; i<runs.size(); i++) {
            Run run = runs.elementAt(i);
            Test t = run.findTest(tname);
            if (t != null) {
               test_id_links.put(tname, run);
               try {
                  History hist = hist_data.get(tname);
                  if (hist == null) {
                     hist = new History(tname);
                     hist_data.put(tname, hist);
                     hist_datav.add(hist);
                  }
                  for (int z = 0; z<t.data.size(); z++) {
                     Row r = t.data.elementAt(z);
                     HistRow csv = hist.findRow(r.getShortDescKey());
                     if (csv == null) {
                        csv = new HistRow(r);
                        hist.addRow(csv);
                     }
                     String score =  t.data.elementAt(z).getScore();
                     csv.csv.append(i + kpi.out_sep + score + System.lineSeparator());
                     csv.scores.add(Double.valueOf(score));
                  }
               }
               catch (Exception eee) {
                  eee.printStackTrace();
               }
            }
         }
      }

      StringBuffer scores = new StringBuffer();
      StringBuffer plots = new StringBuffer();
      StringBuffer groups = new StringBuffer();
      StringBuffer runs_rows = new StringBuffer();

      // For all per-test history, print out csv files
      for (History hist : hist_datav) {
         String hk = hist.getName();
         Hashtable<String, Vector> groupsh = new Hashtable();
         Vector<String> groupsn = new Vector();
         for (HistRow csv : hist.csv) {
            String ck = csv.getName();
            String title = csv.getTitle();
            String units = csv.getUnits();
            String g = csv.getGraphGroup();

            if (!(g.equals("NA") || units.equals(""))) {
               Vector<HistRow> gv = groupsh.get(g);
               if (gv == null) {
                  gv = new Vector();
                  groupsh.put(g, gv);
                  groupsn.add(g);
               }
               gv.add(csv);
            }

            if (units.equals("NA") || units.equals("")) {
               units = "Data";
            }
            try {
               String cf = dir + File.separator + hk + "::" + ck + ".csv";
               FileWriter f = new FileWriter(cf);
               f.write(csv.csv.toString());
               f.close();
               csv.setFname(cf);

               ShellExec exec = new ShellExec(true, true);
               int rv = exec.execute("gnuplot", null, true,
                                     "-e", "set ylabel \"" + units + "\"",
                                     "-e", "filename='" + cf + "'",
                                     "-e", "set title '" + title + "'",
                                     "default.plot");
               if (rv != 0) {
                  System.out.println("gnuplot for filename: " + cf + " rv: " + rv);
                  System.out.println(exec.getOutput());
                  System.out.println(exec.getError());
               }

               File png = new File("plot.png");
               String npng = hk + "::" + ck + ".png";
               png.renameTo(new File(dir + File.separator + npng));

               exec = new ShellExec(true, true);
               rv = exec.execute("gnuplot", null, true, "-e", "filename='" + cf + "'",
                                     "mini.plot");
               if (rv != 0) {
                  System.out.println("mini gnuplot for filename: " + cf + " rv: " + rv);
                  System.out.println(exec.getOutput());
                  System.out.println(exec.getError());
               }

               png = new File("plot.png");
               String npngt = hk + "::" + ck + "-thumb.png";
               png.renameTo(new File(dir + File.separator + npngt));

               String hk_str = hk;
               Run last = test_id_links.get(hk);
               if (last != null) {
                  hk_str = "<a href=\"" + last.getName() + "/" + hk + "/index.html\">" + hk + "</a>";
               }

               StringBuffer change = new StringBuffer();
               Double cur = csv.scores.elementAt(csv.scores.size() - 1);
               change.append("Last Value: " + toStringNum(cur, 2));
               if (csv.scores.size() > 1) {
                  Double prev = csv.scores.elementAt(csv.scores.size() - 2);
                  change.append("<br>Delta for last run: " + toStringNum((cur - prev), 2));
                  if (cur != 0) {
                     change.append("<br>Percentage change: " + toStringNum(100.0 * ((cur - prev) / cur), 2) + "%");
                  }
               }

               String row_str = ("<tr><td>" + hk_str + "</td><td>" + title + "</td><td><a href=\"" + npng + "\"><img src=\"" + npngt + "\"></a></td><td>"
                                 + change + "</td></tr>\n");
               if (csv.getPriority() >= 100) {
                  scores.append(row_str);
               }
               else {
                  plots.append(row_str);
               }
            }
            catch (Exception ee) {
               ee.printStackTrace();
            }
         }

         // Graph groups
         for (String g : groupsn) {
            Vector<HistRow> datasets = groupsh.get(g);
            if (datasets.size() < 2) {
               continue; // group of 1 doesn't count
            }

            HistRow csv0 = datasets.elementAt(0);
            String title = g;
            String units = csv0.getUnits();

            // Don't group scores
            if (units.equalsIgnoreCase("Score")) {
               continue;
            }

            if (units.equals("NA") || units.equals("")) {
               units = "Data";
            }

            System.out.println("title: " + title + " units: " + units);
            try {
               StringBuffer plot = new StringBuffer("plot ");
               StringBuffer mplot = new StringBuffer("plot ");
               boolean first = true;
               for (HistRow csv: datasets) {
                  if (!first) {
                     plot.append(", ");
                     mplot.append(", ");
                  }
                  plot.append("\'" + csv.getFname() + "\' using 1:2 with lines title \'" + csv.getName().replace("_", " ") + "\'");
                  mplot.append("\'" + csv.getFname() + "\' using 1:2 with lines notitle");
                  first = false;
               }

               BufferedReader br = new BufferedReader(new FileReader("default_group.plot"));
               FileWriter f = new FileWriter("tmp.plot");
               String line;
               while ((line = br.readLine()) != null) {
                  f.write(line);
                  f.write(System.lineSeparator());
               }
               f.write(plot.toString());
               f.write(System.lineSeparator());
               f.close();
               br.close();

               //System.out.println("group plot: " + plot);
               ShellExec exec = new ShellExec(true, true);
               int rv = exec.execute("gnuplot", null, true,
                                     "-e", "set ylabel '" + units + "'",
                                     "-e", "set title '" + title + "'",
                                     "tmp.plot");
               if (rv != 0) {
                  System.out.println("gnuplot for group: " + title + " rv: " + rv);
                  System.out.println(exec.getOutput());
                  System.out.println(exec.getError());
               }

               File png = new File("plot.png");
               String npng = hk + "::" + g + ".png";
               png.renameTo(new File(dir + File.separator + npng));

               br = new BufferedReader(new FileReader("mini_group.plot"));
               f = new FileWriter("tmp.plot");
               while ((line = br.readLine()) != null) {
                  f.write(line);
                  f.write(System.lineSeparator());
               }
               f.write(mplot.toString());
               f.write(System.lineSeparator());
               f.close();
               br.close();

               exec = new ShellExec(true, true);
               rv = exec.execute("gnuplot", null, true,
                                 "tmp.plot");
               if (rv != 0) {
                  System.out.println("mini gnuplot for group: " + title + " rv: " + rv);
                  System.out.println(exec.getOutput());
                  System.out.println(exec.getError());
               }

               png = new File("plot.png");
               String npngt = hk + "::" + g + "-thumb.png";
               png.renameTo(new File(dir + File.separator + npngt));

               String hk_str = hk;
               Run last = test_id_links.get(hk);
               if (last != null) {
                  hk_str = "<a href=\"" + last.getName() + "/" + hk + "/index.html\">" + hk + "</a>";
               }

               groups.append("<tr><td>" + hk_str + "</td><td>" + title + "</td><td><a href=\"" + npng + "\"><img src=\"" + npngt + "\"></a></td></tr>\n");

            }
            catch (Exception ee) {
               ee.printStackTrace();
            }
         }
         
      }

      String test_bed = "Test Bed";
      String last_run = "";
      String last_run_kpi_images = "";
      StringBuffer pngs = new StringBuffer();

      boolean cp = true;
      for (int i = 0; i<runs.size(); i++) {
         Run run = runs.elementAt(i);
         test_bed = run.getTestRig();
         String row_text = ("<tr><td>" + i + "</td><td><a href=\"" + run.getName() + "/index.html\">" + run.getName() + "</a></td><td>" + run.getDate()
                            + "</td><td>" + run.getDutHwVer() + "</td><td>" + run.getDutSwVer()
                            + "</td><td>" + run.getDutModelNum() + "</td></tr>\n");
         if (i == (runs.size() - 1)) {
            int png_row_count = 0;
            boolean needs_tr = true;
            last_run = row_text;
            for (Test t : run.testsv) {
               for (String png : t.kpi_images) {
                  if (png.indexOf("-print") >= 0) {
                     continue; // skip the print variants of the image.
                  }
                  if (needs_tr) {
                     pngs.append("<tr>");
                     needs_tr = false;
                  }
                  String img_title = "Test: " + t.getName();
                  String fname = run.getName() + "/" + t.getName() + "/" + png;
                  pngs.append("<td><a href=\"" + fname + "\"><img src=\"" + fname + "\" style='width:400px;max-width:400px' title=\""
                              + img_title + "\"></a></td>\n");
                  png_row_count++;
                  if (png_row_count == 2) {
                     png_row_count = 0;
                     pngs.append("</tr>\n");
                     needs_tr = true;
                  }
               }
            }

            if ((!needs_tr) && pngs.length() > 0) {
               pngs.append("</tr>\n");
            }
         }

         runs_rows.append(row_text);

         if (cp) {
            try {
               String fname;
               copy("CandelaLogo2-90dpi-200x90-trans.png", dir + File.separator + run.getName(), dir);
               copy("candela_swirl_small-72h.png", dir + File.separator + run.getName(), dir);
               copy("canvil.ico", dir + File.separator + run.getName(), dir);
               copy("custom.css", dir + File.separator + run.getName(), dir);
               copy("report.css", dir + File.separator + run.getName(), dir);

               cp = false;
            }
            catch (Exception ee) {
               ee.printStackTrace();
            }
         }
      }

      try {
         // Read in the testbed_template.html and update it with our info
         BufferedReader br = new BufferedReader(new FileReader(new File(kpi.TESTBED_TEMPLATE)));
         String ofile = dir + File.separator + "index.html";
         BufferedWriter bw = new BufferedWriter(new FileWriter(ofile));
         String line;
         while ((line = br.readLine()) != null) {
            line = line.replace("___TITLE___", test_bed + " Report History");
            line = line.replace("___SCORE_RUNS___", scores.toString());
            line = line.replace("___GROUP_GRAPHS___", groups.toString());
            line = line.replace("___DATA_GRAPHS___", plots.toString());
            line = line.replace("___TEST_RUNS___", runs_rows.toString());
            line = line.replace("___LATEST_RUN___", last_run);
            line = line.replace("___LATEST_RUN_PNGS___", pngs.toString());
            bw.write(line);
            bw.write(System.lineSeparator());
         }
         
         br.close();
         bw.close();

         System.out.println("See " + ofile);
      }
      catch (Exception eee) {
         eee.printStackTrace();
      }
   } // ~work()

   public void copy(String fname, String from, String to) throws Exception {
      Path fromp = Paths.get(from + File.separator + fname);
      Path top = Paths.get(to + File.separator + fname);
      Files.copy(fromp, top, StandardCopyOption.REPLACE_EXISTING);
   }
}

class HistRow {
   String fname;
   String name;
   String title = "";
   String units = "";
   String graph_group = "";
   int prio = 0;
   StringBuffer csv = new StringBuffer();
   Vector<Double> scores = new Vector();

   public HistRow(Row r) {
      name = r.getShortDescKey();
      title = r.getShortDesc();
      units = r.getUnits();
      graph_group = r.getGraphGroup();
      prio = r.getPriority();
   }

   int getPriority() {
      return prio;
   }

   String getFname() {
      return fname;
   }

   void setFname(String s) {
      fname = s;
   }

   String getName() {
      return name;
   }

   String getTitle() {
      return title;
   }

   String getUnits() {
      return units;
   }

   String getGraphGroup() {
      return graph_group;
   }
}

class History {
   String name;
   Vector<HistRow> csv = new Vector();
   Hashtable<String, HistRow> csvh = new Hashtable(); // lookup by name

   public History(String n) {
      name = n;
   }

   public String getName() {
      return name;
   }

   HistRow findRow(String n) {
      //System.out.println("findCsv, n: " + n);
      return csvh.get(n);
   }

   void addRow(HistRow r) {
      csv.add(r);
      csvh.put(r.getName(), r);
   }
}

class Row {
   Vector<String> rdata = new Vector();
   String short_desc_key = null;

   String getNotes() {
      return rdata.elementAt(kpi.NOTES_IDX);
   }

   String getUnits() {
      try {
         return rdata.elementAt(kpi.UNITS_IDX);
      }
      catch (Exception e) {
         return "";
      }
   }

   String getGraphGroup() {
      try {
         return rdata.elementAt(kpi.GRAPH_GROUP_IDX);
      }
      catch (Exception e) {
         return "";
      }
   }

   int getPriority() {
      try {
         return Long.valueOf(rdata.elementAt(kpi.PRIORITY_IDX)).intValue();
      }
      catch (Exception e) {
         return 0;
      }
   }

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
   Vector<String> kpi_images = new Vector();

   long date_ms = 0;
   public String date = "NA";
   public String test_rig = "NA";
   public String dut_hw_version = "NA";
   public String dut_sw_version = "NA";
   public String dut_model_num = "NA";
   public String dut_serial_num = "NA";

   public Test(String n) {
      name = n;
   }

   void addKpiImage(String s) {
      kpi_images.add(s);
   }

   long getDateMs() {
      return date_ms;
   }

   String getTestRig() {
      return test_rig;
   }

   String getDutHwVer() {
      return dut_hw_version;
   }

   String getDutSwVer() {
      return dut_sw_version;
   }

   String getDutSerialNum() {
      return dut_serial_num;
   }

   String getDutModelNum() {
      System.out.println("Test: " + getName() + " model-num: " + dut_model_num);
      return dut_model_num;
   }

   String getDate() {
      return date;
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

            if ((data.size() >= 1) && (!last_was_sep) && dut_sw_version.equals("NA")) { // first row is being added
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
               else if (titles.elementAt(idx - 1).equalsIgnoreCase("Date")) {
                  //System.out.println("idx: " + idx + " rtok: " + rtok);
                  date_ms = Long.valueOf(rtok).longValue();
                  date = new Date(date_ms).toString();
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
}//Test


class Run {
   String name;
   Hashtable<String, Test> tests = new Hashtable();
   Vector<Test> testsv = new Vector();

   public Run(String n) {
      name = n;
   }

   Test getFirstTest() {
      return testsv.elementAt(0);
   }

   String getDate() {
      Test t = getFirstTest();
      if (t != null)
         return t.getDate();
      return "";
   }

   long getDateMs() {
      Test t = getFirstTest();
      if (t != null)
         return t.getDateMs();
      return 0;
   }

   String getTestRig() {
      Test t = getFirstTest();
      if (t != null)
         return t.getTestRig();
      return "";
   }

   String getDutHwVer() {
      Test t = getFirstTest();
      if (t != null)
         return t.getDutHwVer();
      return "";
   }

   String getDutSwVer() {
      Test t = getFirstTest();
      if (t != null)
         return t.getDutSwVer();
      return "";
   }

   String getDutModelNum() {
      Test t = getFirstTest();
      if (t != null)
         return t.getDutModelNum();
      return "";
   }

   String getName() {
      return name;
   }

   void addTest(Test t) {
      tests.put(t.getName(), t);
      testsv.add(t);
   }

   Test findTest(String n) {
      return tests.get(n);
   }
}//Run


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
