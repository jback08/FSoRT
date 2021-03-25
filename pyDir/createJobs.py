#!/usr/bin/python

import os
import random
import sys

def run(inputLabel):
    
    baseDir = '/home/phsdau/FlukaProject/fluka2011_2x_6/flair-2.3/DUNE'
    workDir = '{0}/{1}'.format(baseDir, inputLabel)

    # The name & directory of the template Fluka input file
    template = '{0}/{1}.inp'.format(workDir, inputLabel)
    print 'Template input file {0}'.format(template)

    # Number of jobs (10k events each)
    nJobs = 100

    # Create an overall run script
    runName = 'run{0}Jobs.sh'.format(inputLabel)
    runFile = open(runName, 'w')

    # Common job submission command, specifying options etc..
    # Long queue is 12 hours real time; most jobs should take 2 to 3 hrs
    jobCmd = 'bsub -q long -G nufacgrp'

    for i in range(nJobs):

        jobName = '{0}Job{1}'.format(inputLabel, i)
        jobDir = '{0}/{1}'.format(workDir, jobName)

        # Create directory to store the input and output data files
        if (os.path.isdir(jobDir) == False):
            print 'Creating directory {0}'.format(jobDir)
            os.makedirs(jobDir)

        # Full file (& dir) name for the Fluka input file for this job
        fileName = '{0}/{1}.inp'.format(jobDir, inputLabel)

        # Copy the template file changing only the random seed
        randInt = random.randint(10000000, 99999999)
        createFlukaFile(fileName, template, randInt)

        # Create the job script file. Use a temporary directory for the output
        # files, then copy the output to the data area at the end
        jobFileName = createJobScript(jobName, jobDir, baseDir, workDir, inputLabel, fileName)

        # Put this job file in the run script
        logFileName = '{0}/{1}.log'.format(jobDir, jobName)
        line = '{0} -o {1} \"sh {2}"\n'.format(jobCmd, logFileName, jobFileName)
        runFile.write(line)

        line = 'sleep 2\n'
        runFile.write(line)

    runFile.close()


def createFlukaFile(fileName, template, randInt):

    inFile = open(template, 'r')
    outFile = open(fileName, 'w')
    print 'Creating Fluka file {0} from {1} with rand = {2}'.format(fileName,
                                                                    template,
                                                                    randInt)
    for line in inFile:

        words = line.rstrip('\n').split()
        # Check if the first word contains RANDOMIZ
        if words[0] == 'RANDOMIZ':
            # Change random seed initialisation
            newLine = 'RANDOMIZ          1. {0}.\n'.format(randInt)
            outFile.write(newLine)
        else:
            # Keep the line
            outFile.write(line)

    outFile.close()
    inFile.close()


def createJobScript(jobName, jobDir, baseDir, workDir, inputLabel, fileName):

    # Create the job run script, giving the list of commands to setup the
    # files in a temporary job directory, running Fluka, then copying the output

    jobFileName = '{0}/run.sh'.format(jobDir)
    jobFile = open(jobFileName, 'w')
    
    tmpDir = '/tmp/{0}'.format(jobName)

    # Create temporary directory and copy the input file
    line = 'mkdir {0}\n'.format(tmpDir)
    jobFile.write(line)
    line = 'cd {0}\n'.format(tmpDir)
    jobFile.write(line)
    line = 'cp {0} .\n'.format(fileName)
    jobFile.write(line)
    # Copy the field map
    line = 'cp {0}/FieldMap3D.dat .\n'.format(baseDir)
    jobFile.write(line)

    # Run the executable
    line = '$FLUPRO/flutil/rfluka -e $FLUPRO/flukahp -N0 -M1 {0}\n'.format(inputLabel)
    jobFile.write(line)

    # Copy the usrbin output files to the data directory
    usrbins = ['21', '22', '23', '24', '25', '26', '27', '28', '29', '50']
    usrbStart = 21
    usrbEnd = 50
    for u in range(usrbStart, usrbEnd+1):
        outName = '{0}001_fort.{1}'.format(inputLabel, u)
        line = 'cp {0} {1}/.\n'.format(outName, jobDir)
        jobFile.write(line)

    # Copy the event-by-event energy deposition region text file data
    evtFile = '{0}001_evt.txt'.format(inputLabel)
    evtLine = 'cp {0} {1}/.\n'.format(evtFile, jobDir)
    jobFile.write(evtLine)

    # Remove the temporary directory
    line = 'cd $HOME\n'
    jobFile.write(line)
    line = 'rm -rf {0}'.format(tmpDir)
    jobFile.write(line)

    jobFile.close()

    return jobFileName


if __name__ == "__main__":

    inputLabel = 'DoubleTarget'
    nArg = len(sys.argv)

    if nArg > 1:
        inputLabel = sys.argv[1]

    run(inputLabel)
