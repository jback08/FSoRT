# Script to submit a Fluka simulation run given an input file

import argparse
import os
import math
import platform
import random
import sys

class parameters(object):

    def __init__(self, args):

        # Home directory
        self.home = os.getenv('HOME')
        # Fluka release and base directory, assumed to be in $HOME/app/FlukaArchive/flukaVer
        self.flukaVer = 'fluka4-5.0'
        self.flukaDir = '{0}/app/FlukaArchive/{1}'.format(self.home, self.flukaVer)
        # Location of flair and the working sub-dir containing input files
        self.flairVer = 'flair-3.4-3'
        self.flairDir = '{0}/{1}'.format(self.flukaDir, self.flairVer)
        self.workName = 'FSoRT'
        # Location of input files
        self.inDir = '{0}/{1}'.format(self.flairDir, self.workName)

        # B field parameters file expected by magfld.f
        self.fieldPars = 'FieldPars.dat'
        
        # Scratch area for batch jobs:
        self.user = os.getenv('USER')
        self.scratch = '/pnfs/dune/scratch/users/{0}/FlukaArchive'.format(self.user)
        self.baseJob = '{0}/{1}/{2}'.format(self.scratch, self.flukaVer, self.workName)
        # Name of Fluka "release" tar ball
        self.flukaTarName = 'FlukaInstall.tar.gz'
        self.flukaTarFile = '{0}/{1}'.format(self.baseJob, self.flukaTarName)

        # Proton beam energy (GeV)
        self.beamE = 120.0

        # Beam FWHM size (cm)
        #self.beamFWHM = 2.0*math.sqrt(2.0*math.log(2.0))*self.beamSigma

        # Nominal beam sigma (cm) = r/3, r = 8 mm
        self.beamSigma = 0.2667

        # Nominal beam offset (cm) = zero
        self.beamOffset = 0.0
        
        # Run option: 1 (nominal), 2 wide beam, 3 offset beam
        self.option = int(args.option)

        if self.option == 2:
            # Wider beam
            self.beamSigma = 0.44
        elif self.option == 3:
            # Nominal sigma but offset
            self.beamOffset = 0.677
        
        # Fluka executable
        self.flukaExe = 'flukadpm3'
            
        # Fluka input template file
        self.inName = args.inName
        
        # Number of jobs
        self.nJobs = int(args.nJobs)
        
        # Number of events (protons-on-target POT) per job
        self.nPOT = int(args.nPOT)

        # Job runtime
        self.runtime = args.runtime

        # Job memory
        self.memory = args.memory

        # Batch machine temporary directory location
        self.batchDir = '$_CONDOR_SCRATCH_DIR'

        # Singularity container for DUNE environment
        self.singularity = '/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest'

        # Check cvmfs availability (DUNE and fifeuser), otherwise setup scripts don't work
        self.cvmfs = '\'(TARGET.HAS_Singularity==true&&TARGET.HAS_CVMFS_dune_opensciencegrid_org==true&&TARGET.HAS_CVMFS_larsoft_opensciencegrid_org==true&&TARGET.CVMFS_dune_opensciencegrid_org_REVISION>=1105&&TARGET.HAS_CVMFS_fifeuser1_opensciencegrid_org==true&&TARGET.HAS_CVMFS_fifeuser2_opensciencegrid_org==true&&TARGET.HAS_CVMFS_fifeuser3_opensciencegrid_org==true&&TARGET.HAS_CVMFS_fifeuser4_opensciencegrid_org==true)\''
        

class jobPars(object):

    def __init__(self, baseJob, jobDir, jobName, jobNum):

        self.baseJob = baseJob
        self.jobDir = jobDir
        self.jobName = jobName
        self.jobNum = jobNum

        
def run(pars):

    print('Base job directory = {0}'.format(pars.baseJob))
    if not os.path.exists(pars.baseJob):
        print('Creating {0}'.format(pars.baseJob))
        os.makedirs(pars.baseJob)
        os.chmod(pars.baseJob, 0o744)   
    
    print('inName = {0}, nJobs = {1}, nPOT = {2}'.format(pars.inName, pars.nJobs, pars.nPOT))
    
    # Create tar file containing Fluka release and copy it to the scratch area
    if not os.path.exists(pars.flukaTarFile):
        print('Creating {0}'.format(pars.flukaTarFile))
        # Set the release as the current directory, leaving out flair as well as the
        # lower-level user directories (otherwise they would be needed upon extraction)
        tarCmd = 'tar --exclude={0} -czf {1} -C {2} .'.format(pars.flairVer, pars.flukaTarFile,
                                                              pars.flukaDir, pars.flukaTarName)
        print('tarCmd = {0}'.format(tarCmd))
        os.system(tarCmd)
    else:
        # Tar file has already been created
        print('Using tarball {0}'.format(pars.flukaTarFile))

    runJobs = open('runJobs_{0}_Opt{1}.sh'.format(pars.inName, pars.option), 'w')

    # Loop over the jobs
    for iJ in range(pars.nJobs):
    
        # Run directory for the job
        jobName = '{0}_Opt{1}_{2}'.format(pars.inName, pars.option, iJ)
        jobDir = '{0}/{1}'.format(pars.baseJob, jobName)
        print('JobName = {0}'.format(jobName))
        print('JobDir = {0}'.format(jobDir))
        
        if not os.path.exists(jobDir):
            print('Creating {0}'.format(jobDir))
            os.makedirs(jobDir)
            os.chmod(jobDir, 0o744)

        jPars = jobPars(pars.baseJob, jobDir, jobName, iJ)
            
        # Set horn A field parameter file and Fluka input file
        (inputFile, fieldFile) = createFlukaInput(pars, jPars)
    
        # Now create the script containing the job commands
        jobScript = createJobScript(pars, jPars, inputFile, fieldFile)
    
        # Finally submit the job; for tests, use --timeout=Xm to stop after X minutes (360s for N = 10)
        # 10k events take ~ 2 hours, 50k ~ 10 hours => 10 million events = 200 jobs. Use "12h"
        logFile = '{0}/submitJob.log'.format(jobDir)
    
        # Set job submission command
        jobCmd = 'jobsub_submit -N 1 --resource-provides=usage_model=OPPORTUNISTIC ' \
            '--expected-lifetime={0} --singularity-image={1} ' \
            '--append_condor_requirements={2} --group=dune --memory={3} -L {4} ' \
            'file://{5}\n\n'.format(pars.runtime, pars.singularity, pars.cvmfs,
                                    pars.memory, logFile, jobScript)
        print('jobCmd = {0}'.format(jobCmd))            

        jobLine = '{0}\n'.format(jobCmd)
        runJobs.write(jobLine)

    runJobs.close()
    print('DONE\n')
    
    
def createFlukaInput(pars, jPars):

    # Copy Fluka input file, changing random seed given job number
    oldFileName = '{0}/{1}.inp'.format(pars.inDir, pars.inName)
    newFileName = '{0}/{1}.inp'.format(jPars.jobDir, pars.inName)
    print('Creating {0}\nbased on {1}'.format(newFileName, oldFileName))
    
    if os.path.exists(newFileName):
        os.remove(newFileName)
    newFile = open(newFileName, 'w')

    # Random number using 8 digit integers
    # Seed set using input file name and job number
    random.seed(a=oldFileName+str(jPars.jobNum))
    randInt = random.randint(10000000, 99999999)
  
    with open(oldFileName, 'r') as f:
        for line in f:
            if 'RANDOMIZ' in line:
                newFile.write('{0:<10}{1:>10.0f}{2:>10.0f}\n'.format('RANDOMIZ', 1, randInt))
            elif 'START' in line:
                # Number of events
                newFile.write('{0:<10}{1:>10.1f}\n'.format('START', pars.nPOT))
            elif 'SOURCE' in line:
                # Proton beam source parameters
                print('Opt = {0}'.format(pars.option))
                print('sigma = {0}, offset = {1}'.format(pars.beamSigma, pars.beamOffset))
                newLine = '{0:<10}{1:>10.0f}{2:>10.4f}{3:>10.4f}{4:>10}{5:>10}\n'.format('SOURCE', pars.option*1.0,
                                                                                         pars.beamSigma, pars.beamOffset,
                                                                                         '$bafHoleR', '$bRingOR')
                newFile.write(newLine)
            else:
                # Copy line unchanged
                newFile.write(line)
    
    newFile.close()

    # Copy horn field parameters to scratch job directory
    fieldFile = '{0}/{1}'.format(pars.inDir, pars.fieldPars)
    fieldCopy = '{0}/{1}'.format(jPars.jobDir, pars.fieldPars)
    print('Copying {0}\nto {1}'.format(fieldFile, fieldCopy))
    os.system('cp -f {0} {1}'.format(fieldFile, fieldCopy))
    
    # Return copied filenames
    return (newFileName, fieldCopy)


def createJobScript(pars, jPars, inputFile, fieldFile):

    jobScript = '{0}/job{1}.sh'.format(jPars.jobDir, jPars.jobName)
    print('Creating job script {0}'.format(jobScript))
    if os.path.exists(jobScript):
        os.remove(jobScript)
    jobFile = open(jobScript, 'w')

    # Setup job environment and compiler
    jobFile.write('date\n')
    jobFile.write('source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups\n')
    jobFile.write('setup ifdhc\n')
    jobFile.write('source /cvmfs/sft.cern.ch/lcg/releases/gcc/12.1.0/x86_64-centos7/setup.sh\n\n')
    # Limit copying attempts to avoid stalled jobs
    jobFile.write('export IFDH_CP_MAXRETRIES=2\n')
    
    jobFile.write('echo Batch dir is {0}'.format(pars.batchDir))
    
    # Copy Fluka release tarball from job pnfs area to batch machine local scratch area
    batchTarFile = '{0}/{1}'.format(pars.batchDir, pars.flukaTarName)
    jobFile.write('echo HereA: $_CONDOR_SCRATCH_DIR\n')
    jobFile.write('ifdh cp {0} {1}\n'.format(pars.flukaTarFile, batchTarFile))
    jobFile.write('echo HereB: $_CONDOR_SCRATCH_DIR\n')        
    jobFile.write('tar -xzf {0} -C {1}\n\n'.format(batchTarFile, pars.batchDir))

    jobFile.write('echo Here1: $_CONDOR_SCRATCH_DIR\n')
    
    # Setup Fluka environment
    jobFile.write('export FLUPRO={0}\n'.format(pars.batchDir))
    jobFile.write('echo FLUPRO = $_CONDOR_SCRATCH_DIR\n')
    jobFile.write('echo Here2: $_CONDOR_SCRATCH_DIR\n')

    # Copy Fluka input & field parameter files
    jobFile.write('ifdh cp {0} {1}/{2}\n'.format(inputFile, pars.batchDir, os.path.basename(inputFile)))
    jobFile.write('ifdh cp {0} {1}/{2}\n\n'.format(fieldFile, pars.batchDir, os.path.basename(fieldFile)))

    jobFile.write('echo Here3: $_CONDOR_SCRATCH_DIR\n')
    jobFile.write('ls -tral {0}\n\n'.format(pars.batchDir))

    # Fluka run command
    jobFile.write('cd {0}\n'.format(pars.batchDir))
    runCmd = '$FLUPRO/bin/rfluka -e $FLUPRO/bin/{0} -N0 -M1 {1} \n\n'.format(pars.flukaExe,
                                                                             pars.inName)
    jobFile.write(runCmd)

    jobFile.write('echo Here4\n')

    # List all output (to make sure everything was generated OK)
    jobFile.write('ls -trl {0}\n\n'.format(pars.batchDir))
    
    # Copy output files. First create tarball of all usrbin histograms.
    # Scratch directory is usually /storage/local/data1/condor/execute/dir_X/no_xfer (X = integer)
    getBinList = 'ls {0}*fort* > binList.txt\n'.format(pars.inName)
    jobFile.write(getBinList)
    # Then add event-by-event energy deposition and aperture tracking files
    jobFile.write('ls {0}*.txt >> binList.txt\n'.format(pars.inName))
    # Finally add the log files
    jobFile.write('ls {0}*.log >> binList.txt\n'.format(pars.inName))
    jobFile.write('ls {0}*.out >> binList.txt\n'.format(pars.inName))
    jobFile.write('ls {0}*.err >> binList.txt\n'.format(pars.inName))    
    binTarCmd = 'tar czf binList.tar.gz -T binList.txt\n'
    jobFile.write(binTarCmd)

    jobFile.write('echo Here5\n')

    # List all output (to make sure everything was generated OK)
    jobFile.write('ls -trl {0}\n\n'.format(pars.batchDir))

    # Copy usrbin tarball. We can only extract it after the job has finished, since
    # dCache files are immutable within a job and can't be modified once copied
    jobFile.write('ifdh cp -D {0}/binList.tar.gz {1}/\n'.format(pars.batchDir, jPars.jobDir))

    # Force the job to stop at the end
    jobFile.write('echo Copied all files\n')
    jobFile.write('exit 0\n')
    
    jobFile.close()

    # Make job script executable
    os.chmod(jobScript, 0o744)

    return jobScript


def processArgs(parser):

    parser.add_argument('--option', default=1, type=int, metavar='Opt',
                        help='Choose beam run option: Nominal (1), Wider (2), Offset (3)')
    parser.add_argument('--inName', default='LBNFTgtL150cmJul25', metavar='fileName',
                        help='Input Fluka file label (without .inp extension)')
    parser.add_argument('--nJobs', default=1, type=int, metavar='N', help='Number of jobs')
    parser.add_argument('--nPOT', default=10, type=int, metavar='N', help='Number of POT per job')
    parser.add_argument('--runtime', default='12h', metavar='Xh', help='Job run time')
    parser.add_argument('--memory', default='2000MB', metavar='XMB', help='Job memory')
    

if __name__ == '__main__':

    # Process the command line arguments. Use "python runBaffleFNALJobs.py --help" to see the full list
    parser = argparse.ArgumentParser(description='List of arguments')
    processArgs(parser)
    args = parser.parse_args()
    pars = parameters(args)
    
    run(pars)

