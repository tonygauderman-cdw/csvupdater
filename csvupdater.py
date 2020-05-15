import csv, sys, getopt, yaml, os, logging, logging.handlers


inputfile = ''
outputfile = ''
logger = ''
delimiter = 'comma'
getvalues = False
prefixcol = ''
replacefromcsv = ''

def main(argv):
    global inputfile, outputfile, logger, delimiter, getvalues, prefixcol, replacefromcsv
    logger = logging.getLogger()
    logging.captureWarnings(True)
    if not os.path.isdir("logs"):
        os.makedirs("logs")
    logging.basicConfig(handlers=[logging.handlers.RotatingFileHandler('logs/csvupdater.log', maxBytes=1000000, backupCount=20)],
        format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    logger.critical("csvupdator version 1.0.0")
    sys.stdout.write("csvupdator version 1.0.0\n")
    logger.critical('log level set to ERROR')
    sys.stdout.write("log level set to ERROR\n")

    try:
        opts, args = getopt.getopt(argv, "hi:o:d:l:g:p:r", ["help", "inputfile=", "outputfile=", "delimiter=", "loglevel=",
            "getvalues", "prefixcol=", "replacefromcsv="])

    except:
        logger.critical('FATAL ERROR Invalid Options')
        sys.stdout.write('FATAL ERROR Invalid Options\n')
        logger.critical('csvupdater.exe --inputfile <inputfile> --outputfile <outputfile.txt>')
        sys.stdout.write('csvupdater.exe --inputfile <inputfile> --outputfile <outputfile.txt>\n')
        sys.exit()
    else:
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                sys.stdout.write('csvupdater.exe --deviceclass <deviceclass> --out <outfile.txt>\n')
                sys.exit()
            elif opt in ("-i", "--inputfile"):
                inputfile = arg
            elif opt in ("-o", "--outputfile"):
                outputfile = arg
            elif opt in ("d", "--delimiter"):
                delimiter = arg
            elif opt in ("g", "--getvalues"):
                getvalues = True
            elif opt in ("p", "--prefixcol"):
                prefixcol = arg
            elif opt in ("r", "--replacefromcsv"):
                replacefromcsv = arg
            elif opt in ("l", "--loglevel"):
                loglevel = arg.upper()
                logger.critical('log level requested is ' + loglevel)
                if loglevel == 'DEBUG':
                    logger.setLevel(logging.DEBUG)
                elif loglevel == 'INFO':
                    logger.setLevel(logging.INFO)
                elif loglevel == 'WARNING':
                    logger.setLevel(logging.WARNING)
                elif loglevel == 'ERROR':
                    logger.setLevel(logging.ERROR)
                elif loglevel == 'CRITICAL':
                    logger.setLevel(logging.CRITICAL)
                else:
                    logger.critical('FATAL ERROR')
                    logger.critical('valid log level values are DEBUG, INFO, WARNING, ERROR, and CRITICAL')
                    sys.stdout.write('FATAL ERROR\n')
                    sys.stdout.write('valid log level values are DEBUG, INFO, WARNING, ERROR, and CRITICAL\n')
                    sys.exit()
                logger.critical('log level changed to ' + loglevel)
                sys.stdout.write('log level changed to ' + loglevel + '\n')

            else:
                sys.stdout.write(opt + 'is not a valid option')


    readfile()


def readfile():
    global inputfile, outputfile, logger, getvalues, prefixcol, replacefromcsv
    originalfile = open(inputfile, 'r', newline='', encoding="ISO-8859-1")
    logger.critical("Reading Original File " + inputfile)

    reader = csv.DictReader(originalfile)
    #Dictionary Created from headers of CSV
    headerdictionary = {}
    #Dictionary Created To Write Out YAML file of headers to watch
    valuedictionary = {"Value Mappings": {}}
    rowcount = 0


    #handle fields with numbers at the end as one value in the value mappings file
    logger.info("Reading Input File")
    for fieldname in reader.fieldnames:
        if fieldname[-3:].strip().isnumeric():
            logger.info("Field " + fieldname + " ends in a number.")
            headerdictionary[fieldname[:-3].strip()] = ({"Process": False, "Numeric": True})
            logger.info("Field " + fieldname + " is evaluated as " + fieldname[:-3].strip())
        elif fieldname[-2:].strip().isnumeric():
            logger.info("Field " + fieldname + " ends in a number.")
            headerdictionary[fieldname[:-2].strip()] = ({"Process": False, "Numeric": True})
            logger.info("Field " + fieldname + " is evaluated as " + fieldname[:-2].strip())
        else:
            headerdictionary[fieldname] = ({"Process": False, "Numeric": False})

    logger.critical("Header Dictionary at assignment " + str(headerdictionary))

    if (getvalues == False):
        logger.info("Converting Data In File")
        newfile = open(outputfile, 'w', newline='')
        outwriter = csv.DictWriter(newfile, fieldnames=reader.fieldnames)
        outwriter.writeheader()
    else:
        logger.info("Grabbing Values from File based on valuemappings.yaml")
        sys.stdout.write("Grabbing Values from File based on valuemappings.yaml\n")
    try:
        with open('valuemapping.yaml') as f:
            mappings = yaml.load(f, Loader=yaml.FullLoader)
    except:
        sys.stdout.write("\nvaluemapping.yaml not found. Please Create yaml file per README.md and re-run\n")
        logger.critical("valuemapping.yaml not found.  Please Create yaml file per README.md and re-run")
        sys.exit()

    valuedictionary = mappings

    logger.warning ("Mappings " + str(mappings))

    for key in mappings["Value Mappings"]:
        logger.debug("Value Mappings " + str(key))
        if key in headerdictionary:
            headerdictionary[key]['Process'] = True

    logger.debug("Header Dictionary before modifying data" + str(headerdictionary))

    filehasvalues = False
    for phone in reader:
        logger.debug("phone " + str(phone))
        for header, value in phone.items():
            if header[-3:].strip().isnumeric():
                headerindict = header[:-3].strip()
                headerint = header[-3:].strip()
            elif header[-2:].strip().isnumeric():
                headerindict = header[:-2].strip()
                headerint = header[-2:].strip()
            else:
                headerindict = header
                headerint = 0

            if header == '':
                sys.stdout.write("Cell Data " + str(phone[header]) + " with no Column Header \n")
                sys.exit()

            if (headerdictionary[headerindict]['Process'] == True) and (getvalues == True):
                #if (getvalues == True):
                colheaderdict = mappings["Value Mappings"][headerindict]
                foundinyamlfile = False
                if not colheaderdict:
                    logger.info(header + "list is empty")
                else:
                    for valuepair in colheaderdict:
                        if (phone[header] == valuepair["Old"]):
                            foundinyamlfile = True
                        else:
                            logger.debug("phone header not in yaml file " + str(phone[header]))

                if (foundinyamlfile == False and phone[header] != '' and phone[header] != None):
                    if headerindict in valuedictionary["Value Mappings"]:
                        valueexists = False
                        valueisnone = False
                        if ((valuedictionary["Value Mappings"][headerindict] is None) or
                            (valuedictionary["Value Mappings"][headerindict] == "null")):

                            valueisnone = True
                            logger.info("Value Is None")
                            logger.info("phoneheader " + str(phone[header]) + " headerindict " + headerindict)

                            if prefixcol != '':
                                valuedictionary["Value Mappings"][headerindict] = ({"Old": str(phone[header]),
                                    "New": phone[prefixcol] + " New Value"},)
                            else:
                                valuedictionary["Value Mappings"][headerindict] = ({"Old": str(phone[header]),
                                    "New": "New Value"},)
                            filehasvalues = True

                        else:
                            try:
                                if prefixcol != '':
                                    valuedictionary["Value Mappings"][headerindict] = valuedictionary["Value Mappings"][headerindict] + \
                                        [{"Old": str(phone[header]), "New": phone[prefixcol] + " New Value"}]
                                else:
                                    valuedictionary["Value Mappings"][headerindict] = valuedictionary["Value Mappings"][headerindict] + \
                                        [{"Old": str(phone[header]), "New": "New Value"}]

                            except:
                                if prefixcol != '':
                                    valuedictionary["Value Mappings"][headerindict] = valuedictionary["Value Mappings"][headerindict] + \
                                        ({"Old": str(phone[header]), "New": phone["Device Type"] + " New Value"},)
                                else:
                                    valuedictionary["Value Mappings"][headerindict] = valuedictionary["Value Mappings"][headerindict] + \
                                        ({"Old": str(phone[header]), "New": "New Value"},)

                            filehasvalues = True
                        logger.info("valuedictionary " + str(valuedictionary))
                    else:
                        filehasvalues = True

            elif getvalues == False:

                if (headerdictionary[headerindict]['Process'] == True):

                    colheaderdict = mappings["Value Mappings"][headerindict]

                    if not colheaderdict:
                        logger.info(headerindict + " list is empty")
                    else:
                        foundinheaderdict = False
                        for valuepair in colheaderdict:

                            if phone[header] == valuepair["Old"]:
                                foundinheaderdict = True
                                phone[header] = valuepair["New"]

                        if ((foundinheaderdict == False) and (phone[header] != '') and phone[header] != None):
                            logger.critical(str(phone[header]) + ' not found in valuemapping.yaml')
                            sys.stdout.write("Field " + header + " value " + str(phone[header]) + ' not found in valuemapping.yaml\n')
                            #sys.exit()

                if headerindict in mappings["Calculated Columns"]:
                    for colheader in mappings["Calculated Columns"][headerindict]:

                        if headerint > 0:
                            colheader1 = colheader["Column 1"] + " " + str(headerint)
                            colheader2 = colheader["Column 2"] + " " + str(headerint)
                        else:
                            colheader1 = colheader["Column 1"]
                            colheader2 = colheader["Column 2"]


                        if phone[colheader1][:1] == "\\":
                            columnvalue1 = phone[colheader1][1:]
                        else:
                            columnvalue1 = phone[colheader1]
                        if phone[colheader2][:1] == "\\":
                            columnvalue2 = phone[colheader2][1:]
                        else:
                            columnvalue2 = phone[colheader2]

                        phone[header] = columnvalue1 + " " + columnvalue2

                if headerindict in mappings["Replace From CSV"] and phone[header] != '':
                    for colheader in mappings["Replace From CSV"][header]:
                        originalcolumn = str(colheader["Original"])
                        replacementcolumn = str(colheader["Replacement"])
                        foundreplacement = False

                        csvreplacementfile = open(replacefromcsv, 'r', newline='', encoding="ISO-8859-1")
                        csvreplacement = csv.DictReader(csvreplacementfile)

                        for row in csvreplacement:
                            if phone[header] == row[originalcolumn]:
                                phone[header] = row[replacementcolumn]
                                foundreplacement = True
                        if foundreplacement == False:
                            sys.stdout.write("No value found in csv mapping file for column '" + originalcolumn + "' and value " +
                                phone[header] + '\n')

                if headerindict in mappings["Set To Single Value"]:
                    phone[header] = mappings["Set To Single Value"][headerindict]

        if (getvalues == False):
            outwriter.writerow(phone)
        else:
            newfile = open(outputfile, 'w', newline='')
            if filehasvalues == True:
                #safe_dump avoids writing !!python/tuple to file
                documents = yaml.safe_dump(valuedictionary, newfile)
            else:
                newfile.write("No New Values To Write To File\n")

if __name__ == "__main__":
       main(sys.argv[1:])
