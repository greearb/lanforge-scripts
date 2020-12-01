<! DOCTYPE html>
<html>  

<head>
<title>Testing Report</title>
<head>
    
<?php
//error_reporting(E_ALL);
//ini_set('display_errors', '1');
$results = file_get_contents('report_data.json');
$json = json_decode($results, true);
?>
    
<body bgcolor="grey"> 

<style> 
        .tab1 { 
            tab-size: 8; 
        } 
  
        .tab2 { 
            tab-size: 14; 
        } 
  
        .tab4 { 
            margin-left: 188; 
        } 
    
    div.sanity {
        background-color: lightgray;
        width: 975px;
        border-style: ridge;
        padding: 10px;
        left: 0;
        font-size: 15px;
        line-height: 25px
        
    }
    
 </style> 
       
<header> 
    <h1 style="color:green; font-size:40px; text-align: center">CICD Nightly Sanity Report - <?php echo basename(dirname(__FILE__)) ?></h1>
</header>    
    
<TABLE BORDER="1" WIDTH="1400px" CELLPADDING="4" CELLSPACING="3" Style="background-color: lightgray; font-size:16px">
   <TR>
      <TH COLSPAN="6"><BR><H3>Test Results</H3>
      </TH>
   </TR>
   <TR>
      <TH>Test Case</TH>
      <TH>Description</TH>
      <TH WIDTH="150px">EA8300 Result</TH>
       <TH WIDTH="150px">ECW5211 Result</TH>
       <TH WIDTH="150px">ECW5410 Result</TH>
       <TH WIDTH="150px">EC420 Result</TH>
   </TR>
    
    <TR ALIGN="CENTER">
       <TD></TD>
       <TD ALIGN="LEFT" style="font-weight:bold">New FW Available</TD>
       <TD style="font-weight:bold"><?php echo print_r($json['fw_available']['ea8300'],true) ?></TD>
       <TD style="font-weight:bold"><?php echo print_r($json['fw_available']['ecw5211'],true) ?></TD>
       <TD style="font-weight:bold"><?php echo print_r($json['fw_available']['ecw5410'],true) ?></TD>
       <TD style="font-weight:bold"><?php echo print_r($json['fw_available']['ec420'],true) ?></TD>
   </TR>
       
       <TR ALIGN="CENTER" style="font-weight:bold">
        <TD></TD>
        <TD ALIGN="LEFT" >FW Under Test</TD>
        <TD style="font-size:12px"><?php echo print_r($json['fw_under_test']['ea8300'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['fw_under_test']['ecw5211'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['fw_under_test']['ecw5410'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['fw_under_test']['ec420'],true) ?></TD>
   </TR>

        <TR ALIGN="CENTER" style="font-weight:bold">
        <TD></TD>
        <TD ALIGN="LEFT" >CloudSDK Commit Date</TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ea8300']['date'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ecw5211']['date'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ecw5410']['date'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ec420']['date'],true) ?></TD>
   </TR>

        <TR ALIGN="CENTER" style="font-weight:bold">
        <TD></TD>
        <TD ALIGN="LEFT" >CloudSDK Commit ID</TD>
        <TD style="font-size:10px"><?php echo print_r($json['cloud_sdk']['ea8300']['commitId'],true) ?></TD>
        <TD style="font-size:10px"><?php echo print_r($json['cloud_sdk']['ecw5211']['commitId'],true) ?></TD>
        <TD style="font-size:10px"><?php echo print_r($json['cloud_sdk']['ecw5410']['commitId'],true) ?></TD>
        <TD style="font-size:10px"><?php echo print_r($json['cloud_sdk']['ec420']['commitId'],true) ?></TD>
   </TR>

        <TR ALIGN="CENTER" style="font-weight:bold">
        <TD></TD>
        <TD ALIGN="LEFT" >CloudSDK Project Version</TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ea8300']['projectVersion'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ecw5211']['projectVersion'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ecw5410']['projectVersion'],true) ?></TD>
        <TD style="font-size:12px"><?php echo print_r($json['cloud_sdk']['ec420']['projectVersion'],true) ?></TD>
   </TR>
       
       <TR ALIGN="CENTER" style="font-weight:bold">
        <TD></TD>
        <TD ALIGN="LEFT">Test Pass Rate</TD>
        <TD style="font-size:14px"><?php echo print_r($json['pass_percent']['ea8300'],true) ?></TD>
        <TD style="font-size:14px"><?php echo print_r($json['pass_percent']['ecw5211'],true) ?></TD>
        <TD style="font-size:14px"><?php echo print_r($json['pass_percent']['ecw5410'],true) ?></TD>
        <TD style="font-size:14px"><?php echo print_r($json['pass_percent']['ec420'],true) ?></TD>
   </TR>

      <TR ALIGN="CENTER">
      <TD>5540</TD>
      <TD ALIGN="LEFT">Get CloudSDK Version with API</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5540'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ecw5211']['5540'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ecw5410']['5540'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ec420']['5540'],true) ?></TD>
   </TR>

    <TR ALIGN="CENTER">
      <TD>2233</TD>
      <TD ALIGN="LEFT">AP Upgrade Successful</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['2233'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ecw5211']['2233'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ecw5410']['2233'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ec420']['2233'],true) ?></TD>
   </TR>
       
    <TR ALIGN="CENTER">
      <TD>5247</TD>
      <TD ALIGN="LEFT">CloudSDK Reports Correct FW</TD>
       <TD><?php echo print_r($json['tests']['ea8300']['5247'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ecw5211']['5247'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ecw5410']['5247'],true) ?></TD>
       <TD><?php echo print_r($json['tests']['ec420']['5247'],true) ?></TD>
   </TR>
       
    <TR ALIGN="CENTER">
      <TD>5222</TD>
      <TD ALIGN="LEFT">AP-CloudSDK Connection Active </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5222'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5222'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5222'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5222'],true) ?></TD>
   </TR>

       <TR ALIGN="CENTER">
      <TD>5541</TD>
      <TD ALIGN="LEFT">CloudSDK Pushes Correct AP Profile - Bridge Mode </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5541'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5541'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5541'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5541'],true) ?></TD>
   </TR>

   <TR ALIGN="CENTER">
      <TD>5544</TD>
      <TD ALIGN="LEFT">AP Applies Correct AP Profile - Bridge Mode </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5544'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5544'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5544'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5544'],true) ?></TD>
   </TR>

    <TR ALIGN="CENTER">
      <TD>5214</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA2-EAP - Bridge Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5214'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5214'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5214'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5214'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>2237</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA2 - Bridge Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['2237'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['2237'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['2237'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['2237'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>2420</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA - Bridge Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['2420'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['2420'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['2420'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['2420'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5215</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA2-EAP - Bridge Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5215'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5215'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5215'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5215'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>2236</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA2 - Bridge Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['2236'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['2236'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['2236'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['2236'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>2419</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA - Bridge Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['2419'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['2419'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['2419'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['2419'],true) ?></TD> 

        <TR ALIGN="CENTER">
      <TD>5542</TD>
      <TD ALIGN="LEFT">CloudSDK Pushes Correct AP Profile - NAT Mode </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5542'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5542'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5542'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5542'],true) ?></TD>
   </TR>

   <TR ALIGN="CENTER">
      <TD>5545</TD>
      <TD ALIGN="LEFT">AP Applies Correct AP Profile - NAT Mode </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5545'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5545'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5545'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5545'],true) ?></TD>
   </TR>
        <TR ALIGN="CENTER">
      <TD>5216</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA2-EAP - NAT Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5216'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5216'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5216'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5216'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>4325</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA2 - NAT Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['4325'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['4325'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['4325'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['4325'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>4323</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA - NAT Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['4323'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['4323'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['4323'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['4323'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5217</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA2-EAP - NAT Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5217'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5217'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5217'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5217'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>4326</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA2 - NAT Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['4326'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['4326'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['4326'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['4326'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>4324</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA - NAT Mode</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['4324'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['4324'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['4324'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['4324'],true) ?></TD>    
   </TR>
        <TR ALIGN="CENTER">
      <TD>5543</TD>
      <TD ALIGN="LEFT">CloudSDK Pushes Correct AP Profile - Custom VLAN </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5543'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5543'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5543'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5543'],true) ?></TD>
   </TR>

   <TR ALIGN="CENTER">
      <TD>5546</TD>
      <TD ALIGN="LEFT">AP Applies Correct AP Profile - Custom VLAN </TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5546'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5546'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5546'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5546'],true) ?></TD>
   </TR>

        <TR ALIGN="CENTER">
      <TD>5253</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA2-EAP - Custom VLAN</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5253'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5253'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5253'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5253'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5251</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA2 - Custom VLAN</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5251'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5251'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5251'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5251'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5252</TD>
      <TD ALIGN="LEFT">Client connectivity to 2.4 GHz WPA - Custom VLAN</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5252'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5252'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5252'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5252'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5250</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA2-EAP - Custom VLAN</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5250'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5250'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5250'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5250'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5248</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA2 - Custom VLAN</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5248'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5248'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5248'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5248'],true) ?></TD>
   </TR>
    <TR ALIGN="CENTER">
      <TD>5249</TD>
      <TD ALIGN="LEFT">Client connectivity to 5 GHz WPA - Custom VLAN</TD>
      <TD><?php echo print_r($json['tests']['ea8300']['5249'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5211']['5249'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ecw5410']['5249'],true) ?></TD>
        <TD><?php echo print_r($json['tests']['ec420']['5249'],true) ?></TD>
        </TR>
</TABLE> 
    
</body>