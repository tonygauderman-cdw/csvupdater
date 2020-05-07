import csv, sys, getopt, yaml, logging, logging.handlers


inputfile = ''
outputfile = ''
logger = ''
delimiter = 'comma'
getvalues = False

def main(argv):
    global inputfile, outputfile, logger, delimiter, getvalues
    logger = logging.getLogger()
    logging.captureWarnings(True)
    logging.basicConfig(handlers=[logging.handlers.RotatingFileHandler('csvupdater.log', maxBytes=1000000, backupCount=20)],
        format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    logger.critical("csvupdator version 1.0.0")
    sys.stdout.write("csvupdator version 1.0.0\n")
    logger.critical('log level set to ERROR')
    sys.stdout.write("log level set to ERROR\n")

    try:
        opts, args = getopt.getopt(argv, "hi:o:d:l:g", ["help", "inputfile=", "outputfile=", "delimiter=", "loglevel=", "getvalues"])

    except:
        logger.critical('FATAL ERROR Invalid Options')
        sys.stdout.write('FATAL ERROR Invalid Options\n')
        logger.critical('csvupdater.exe --inputfile <inputfile> --outputfile <outputfile.txt>')
        sys.stdout.write('csvupdater.exe --inputfile <inputfile> --outputfile <outputfile.txt>\n')
        sys.exit()
    else:
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                #logger.critical(
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
    global inputfile, outputfile, logger, getvalues
    originalfile = open(inputfile, 'r', newline='')
    logger.critical("Reading Original File")

    reader = csv.DictReader(originalfile)
    #Dictionary Created from headers of CSV
    headerdictionary = {}
    #Dictionary Created To Write Out YAML file of headers to watch
    valuedictionary = {}
    rowcount = 0

    for fieldname in reader.fieldnames:
        logger.debug("fieldname " + str(fieldname))
        headerdictionary[fieldname] = False

    logger.debug("Header Dictionary at assignment " + str(headerdictionary))

    if (getvalues == False):
        logger.info("Converting Data In File")
        sys.stdout.write("Converting Data In File\n")
        newfile = open(outputfile, 'w', newline='')
        outwriter = csv.DictWriter(newfile, fieldnames=reader.fieldnames)
        outwriter.writeheader()
    else:
        logger.info("Grabbing Values from File based on valuemappings.yaml")
        sys.stdout.write("Grabbing Values from File based on valuemappings.yaml\n")

    with open('valuemapping.yaml') as f:
        mappings = yaml.load(f, Loader=yaml.FullLoader)
    logger.warning ("Mappings " + str(mappings))

    for key in mappings["Value Mappings"]:
        logger.debug("Value Mappings " + str(key))
        headerdictionary[key] = True

    logger.debug("Header Dictionary before modifying data" + str(headerdictionary))

    for phone in reader:
        logger.debug("phone " + str(phone))
        for header, value in phone.items():
            if headerdictionary[header] == None:
                sys.stdout.write("Cell Data with no Column Header \n")
                sys.exit()
            if headerdictionary[header] == True:
                if (getvalues == True):
                    colheaderdict = mappings["Value Mappings"][header]
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
                        #valuedictionary.append(header)
                        #valuedictionary[header] = ({"Old": "Old", "New": "New"}, {"Old": "Old2", "New": "New2"})
                        #valuedictionary[header] =  valuedictionary[header] + ({"Old": "Old3", "New": "New3"},)
                        try:
                            valueexists = False
                            for value in valuedictionary[header]:
                                #sys.stdout.write('str-phone-header ' + str(phone[header]) + '\n')
                                #sys.stdout.write('value ' + value + '\n')
                                if (value == phone[header]):
                                    valueexists = True
                            if (valueexists == False):
                                valuedictionary[header].append(phone[header])
                            logger.debug("Value Dictionary After Append = " + str(valuedictionary))
                        except:
                            valuedictionary[header] = [phone[header]]
                            logger.debug("Value Dictionary After Create = " + str(valuedictionary))

                else:

                    colheaderdict = mappings["Value Mappings"][header]
                    if not colheaderdict:
                        logger.info(header + " list is empty")
                    else:
                        foundinheaderdict = False
                        for valuepair in colheaderdict:
                            #
                            try:
                                if ((phone[header] == valuepair["Old"]) and (phone[header] != '')):
                                    logger.info("Old Value " + valuepair["Old"])
                                    foundinheaderdict = True
                                    logger.info(str(foundinheaderdict) + ' found in valuemapping.yaml')
                            except:
                                logger.critical(str(header) + " " + phone[header] + ' is listed in valuemapping.yaml but does '
                                    'not have an Old: value')
                                sys.stdout.write(str(header) + " " + phone[header] + ' is listed in valuemapping.yaml but does '
                                    'not have an Old: value\n')
                                sys.exit()
                            else:
                                if ((phone[header] == valuepair["Old"]) and (phone[header] != '')):
                                    try:
                                        logger.info("New Value " + valuepair["New"])
                                        phone[header] = valuepair["New"]
                                    except:
                                        logger.critical("No New Value for " + str(header) + ' Value ' + valuepair["Old"])
                                        sys.stdout.write("No New Value for " + str(header) + ' Value ' + valuepair["Old"] + '\n')
                                        sys.exit()
                        if ((foundinheaderdict == False) and (phone[header] != '')):
                            logger.critical(phone[header] + ' not found in valuemapping.yaml')
                            sys.stdout.write(phone[header] + ' not found in valuemapping.yaml\n')
                            sys.exit()
        if (getvalues == False):
            outwriter.writerow(phone)
        else:
            newfile = open(outputfile, 'w', newline='')
            documents = yaml.dump(valuedictionary, newfile)

if __name__ == "__main__":
       main(sys.argv[1:])
