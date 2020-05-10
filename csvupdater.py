import csv, sys, getopt, yaml, os, logging, logging.handlers


inputfile = ''
outputfile = ''
logger = ''
delimiter = 'comma'
getvalues = False
prefixcol = ''

def main(argv):
    global inputfile, outputfile, logger, delimiter, getvalues, prefixcol
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
        opts, args = getopt.getopt(argv, "hi:o:d:l:g:p", ["help", "inputfile=", "outputfile=", "delimiter=", "loglevel=",
            "getvalues", "prefixcol="])

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
    global inputfile, outputfile, logger, getvalues, prefixcol
    originalfile = open(inputfile, 'r', newline='', encoding="ISO-8859-1")
    logger.critical("Reading Original File")

    reader = csv.DictReader(originalfile)
    #Dictionary Created from headers of CSV
    headerdictionary = {}
    #Dictionary Created To Write Out YAML file of headers to watch
    valuedictionary = {"Value Mappings": {}}
    rowcount = 0

    for fieldname in reader.fieldnames:
        logger.debug("fieldname " + str(fieldname))

        #commented out for numeric grouping
        #headerdictionary[fieldname] = False

        #new block for numeric grouping
        if fieldname[-3:].strip().isnumeric():
            #sys.stdout.write("field name " + fieldname + " " + fieldname[-3:].strip() + '\n')
            headerdictionary[fieldname[:-3].strip()] = ({"Process": False, "Numeric": True})
        elif fieldname[-2:].strip().isnumeric():
            #sys.stdout.write("field name " + fieldname + " " + fieldname[-2:].strip() + '\n')
            headerdictionary[fieldname[:-2].strip()] = ({"Process": False, "Numeric": True})
        else:
            headerdictionary[fieldname] = ({"Process": False, "Numeric": False})

    logger.critical("Header Dictionary at assignment " + str(headerdictionary))

    if (getvalues == False):
        logger.info("Converting Data In File")
        sys.stdout.write("Converting Data In File\n")
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

    #added to try and write out a whole new file...
    #sys.stdout.write(str(valuedictionary) + '\n')
    valuedictionary = mappings
    #sys.stdout.write(str(valuedictionary) + '\n')

    logger.warning ("Mappings " + str(mappings))
    #sys.stdout.write ("Mappings " + str(mappings) + '\n')

    for key in mappings["Value Mappings"]:
        logger.debug("Value Mappings " + str(key))
        if key in headerdictionary:
            headerdictionary[key]['Process'] = True

    logger.debug("Header Dictionary before modifying data" + str(headerdictionary))
    #sys.stdout.write("Header Dictionary before modifying data " + str(headerdictionary) + '\n')

    filehasvalues = False
    for phone in reader:
        logger.debug("phone " + str(phone))
        for header, value in phone.items():
            #added for numeric processing
            #sys.stdout.write("header " + str(header) + '\n')
            if header[-3:].strip().isnumeric():
                #sys.stdout.write(str(headerdictionary[header[:-3].strip()]) + '\n')
                headerindict = header[:-3].strip()
            elif header[-2:].strip().isnumeric():
                #sys.stdout.write(str(headerdictionary[header[:-2].strip()]) + '\n')
                headerindict = header[:-2].strip()
            else:
                headerindict = header
            #sys.stdout.write(str(headerdictionary[header[:-3].strip()]) + '\n')
            #sys.stdout.write("headerindict " + str(headerindict) + '\n')
            #if headerdictionary[header] == None:
            if header == '':
                sys.stdout.write("Cell Data with no Column Header \n")
                sys.exit()

            if headerdictionary[headerindict]['Process'] == True:
                if (getvalues == True):
                    colheaderdict = mappings["Value Mappings"][headerindict]
                    foundinyamlfile = False
                    if not colheaderdict:
                        logger.info(header + "list is empty")
                    else:
                        for valuepair in colheaderdict:
                            if (phone[header] == valuepair["Old"]):
                                foundinyamlfile = True
                            else:
                                logger.debug("phone header not in yaml file " + phone[header])

                    if (foundinyamlfile == False and phone[header] != ''):

                        #if header in valuedictionary["Value Mappings"]:
                        if headerindict in valuedictionary["Value Mappings"]:
                            valueexists = False
                            valueisnone = False
                            #sys.stdout.write("headerindict " + headerindict + '\n')
                            #sys.stdout.write(str(valuedictionary["Value Mappings"][headerindict]) + '\n')
                            if ((valuedictionary["Value Mappings"][headerindict] is None) or
                                (valuedictionary["Value Mappings"][headerindict] == "null")):
                                valueisnone = True
                                logger.info("Value Is None")
                                logger.info("phoneheader " + phone[header] + " headerindict " + headerindict)
                                if prefixcol != '':
                                    valuedictionary["Value Mappings"][headerindict] = ({"Old": str(phone[header]),
                                        "New": phone["Device Type"] + " New Value"},)
                                else:
                                    valuedictionary["Value Mappings"][headerindict] = ({"Old": str(phone[header]),
                                        "New": "New Value"},)
                                #sys.stdout.write(str(valuedictionary))
                                filehasvalues = True
                            else:
                                #sys.stdout.write (str(valuedictionary["Value Mappings"][headerindict]) + '\n')
                                #sys.stdout.write(str([{"Old": str(phone[header]), "New": "NewValue"}]) + '\n')
                                try:
                                    if prefixcol != '':
                                        valuedictionary["Value Mappings"][headerindict] = valuedictionary["Value Mappings"][headerindict] + \
                                            [{"Old": str(phone[header]), "New": phone["Device Type"] + " New Value"}]
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


                                #for agevaluepair in valuedictionary["Value Mappings"][headerindict]:
                                    #sys.stdout.write("phone header " + str(phone[header]) + " filevalue " + str(agevaluepair["Old"]) + '\n')
                                #    if phone[header] == agevaluepair["Old"]:
                                #        sys.stdout.write("match\n")
                                #        valueexists = True
                                #filehasvalues = True




                            #if valueexists == False and valueisnone == True:
                            #    valuedictionary["Value Mappings"][headerindict] = ({"Old": str(phone[header]), "New": "NewValue"},)
                            #elif valueexists == False:
                            #    valuedictionary["Value Mappings"][headerindict] = valuedictionary["Value Mappings"][headerindict] + ({"Old": str(phone[header]), "New": "NewValue"},)
                        else:
                            #valuedictionary["Value Mappings"][headerindict] = ({"Old": str(phone[header]), "New": "NewValue"},)
                            filehasvalues = True

                else:
                    #start with headerindict logic
                    colheaderdict = mappings["Value Mappings"][headerindict]
                    if not colheaderdict:
                        logger.info(headerindict + " list is empty")
                    else:
                        foundinheaderdict = False
                        for valuepair in colheaderdict:
                            #add logic to check for actual header value and handle numeric..
                            #

                            sys.stdout.write("headerindict " + headerindict + '\n')
                            sys.stdout.write("colheaderdict " + str(colheaderdict) + '\n')
                            sys.stdout.write("valuepair " + str(valuepair) + '\n')
                            sys.stdout.write("phoneheaderindict " + phone[header] + " valuepair old " + valuepair["Old"] + '\n')

                            if header[-3:].strip().isnumeric():
                                headertolookfor = header[:-3].strip()
                            elif header[-2:].strip().isnumeric():
                                headertolookfor = header[:-2].strip()
                            else:
                                headertolookfor = header
                            if (headertolookfor == headerindict):
                                sys.stdout.write("header to look for " + headertolookfor + '\n')
                                sys.stdout.write("Old value pair " + valuepair["Old"] + '\n')
                                if phone[header] == valuepair["Old"]:
                                    foundinheaderdict = True
                                    logger.info(str(phone[header]) + ' found in valuemapping.yaml')
                                    sys.stdout.write(str(phone[header]) + ' found in valuemapping.yaml\n')
                                    phone[header] = valuepair["New"]

                            #try:
                            #    if ((phone[headerindict] == valuepair["Old"]) and (phone[headerindict] != '')):
                            #        logger.info("Old Value " + valuepair["Old"])
                            #        foundinheaderdict = True
                            #        logger.info(str(foundinheaderdict) + ' found in valuemapping.yaml')
                            #except:
                            #    logger.critical("Header " + str(header) + " and value " + phone[header] +
                            #        ' not formatted in valuemapping.yaml file properly')
                            #    sys.stdout.write("Header " + str(header) + " and value " + phone[header] +
                            #        ' not formatted in valuemapping.yaml file properly')
                            #    sys.exit()
                            #else:
                            #    if ((phone[headerindict] == valuepair["Old"]) and (phone[headerindict] != '')):
                            #        try:
                            #            logger.info("New Value " + valuepair["New"])
                            #            phone[headerindict] = valuepair["New"]
                            #        except:
                            #            logger.critical("No New Value for " + str(headerindict) + ' Value ' + valuepair["Old"])
                            #            sys.stdout.write("No New Value for " + str(headerindict) + ' Value ' + valuepair["Old"] + '\n')
                            #            sys.exit()
                        if ((foundinheaderdict == False) and (phone[header] != '')):
                            logger.critical(phone[header] + ' not found in valuemapping.yaml')
                            sys.stdout.write(phone[header] + ' not found in valuemapping.yaml\n')
                            sys.exit()

        #sys.stdout.write("phone line " + str(phone) + '\n')
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
