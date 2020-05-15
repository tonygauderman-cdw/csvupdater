csvupdater version 1.0.0

This command line tool allows you to read in a CSV file and process column headers by reading in a valuemapping.yaml file
to define what column headers are interesting.  You can then modify old and new values in the valuemapping.yaml file and
run the tool again to replace the values in the interesting column headers with different values as defined in the file.


Files are processed based on valuemapping.yaml, which is formatted as below where the values under "Value Mappings" or
"Calculated Columns" are column headers in the CSV file.  Column headers in "Value Mappings" can be processed against the
CSV file with --getvalues which generates the New/Old pair.  The New value would be updated to the value the Old value
should be replaced with when the script is run without --getvalues.  The CSV column headers in "Calculated Columns" are
replaced by the values in the columns in the associated "Column 1" and "Column 2".  The values are concatenated with a
space added between them.  If the first character in either string is a \ it is stripped (i.e. \+18005532447 becomes
+18005532447)

Value Mappings:
  Busy Lamp Field Directory Number: null
  CSS:
  - New: Cisco 8851 New Value
    Old: CSS-AAH-LV-Device
  - New: Cisco 8851 New Value
    Old: CSS-AAH-GB-Device
Calculated Columns:
  Description:
  - Column 1: Alerting Name 1
    Column 2: Directory Number 1


Required Parameters:
--inputfile     CSV file to read
--outputfile    CSV or yaml file to write
--delimiter     define delimiter as tab or comma (not tested and likely not working yet)

Optional Parameters:
--getvalues     Used to process the interesting column headers in the valuemapping.yaml file and write values from those
                headers as values into the valuemapping.yaml file.  This will read the valuemapping.yaml file and write
                out a new file based on --outputfile that contains all the values in valuemapping.yaml and new values
                that weren't already in the file

--prefixcol     Used to take a value from a single column in the file and prefix it on the default "New Value" that is written
                This has no impact unless paired with --getvalue



Use:
sqltocsv.exe --version <cucm_major_version> --sql <file_with_sql_statement> --out <file_to_write_to>

To create or update valuemapping.yaml based on values in the interesting columns that are not already in the file and prefix "Device Type" to new values
csvupdateer.exe --inputfile ccclusterexports/export8851aah_04222020132608-clean-AAH.csv --outputfile out.yaml --prefixcol "Device Type" --getvalues

To create or update valuemapping.yaml based on values in the interesting columns that are not already in the file
csvupdateer.exe --inputfile ccclusterexports/export8851aah_04222020132608-clean-AAH.csv --outputfile out.yaml --getvalues

To read in a CSV file and process it with values in the valuemapping.yaml file
csvupdateer.exe --inputfile ccclusterexports/export8851aah_04222020132608-clean-AAH.csv --outputfile out.yaml
