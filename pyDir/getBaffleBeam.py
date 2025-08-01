import argparse
import math
import numpy

pi = math.acos(-1.0)
twoPi = 2.0*pi
invTwoPi = 1.0/twoPi

# Gaussian function parameters
class gaussPars(object):

    def __init__(self, mux, muy, sigmax, sigmay, frac):
        self.mux = mux
        self.muy = muy
        self.sigmax = sigmax
        self.sigmay = sigmay
        self.frac = frac
        self.dSigma = 1e-3 # sigma accuracy
        self.dOffset = 1e-3 # offset accuracy
        self.epsilon = 1e-6 # area fraction accuracy


# Integration ranges
class intRanges(object):

    def __init__(self, minR, maxR, nR, minPhi, maxPhi, nPhi):

        self.minR = minR
        self.maxR = maxR
        self.nR = nR
        self.rangeR = maxR - minR
        self.halfRangeR = 0.5*self.rangeR
        self.meanR = 0.5*(minR + maxR)
        self.dR = self.rangeR/(nR*1.0)

        self.minPhi = minPhi
        self.maxPhi = maxPhi
        self.nPhi = nPhi
        self.rangePhi = maxPhi - minPhi
        self.halfRangePhi = 0.5*self.rangePhi
        self.meanPhi = 0.5*(minPhi + maxPhi)
        self.dPhi = self.rangePhi/(nPhi*1.0)

        # Weight conversion scale factor.
        # Converts (-1, 1) Legendre weight integral limits to (min, max)
        self.intFactor = self.halfRangeR*self.halfRangePhi
        

def calcGaussLegendreWeights(numPoints):

    m = int((numPoints+1)/2)
    dnumPoints = numPoints*1.0
    dnumPointsPlusHalf = dnumPoints + 0.5
    weightsPrecision = 1e-6

    abscissas = numpy.zeros(numPoints)
    weights = numpy.zeros(numPoints)
    
    for i in range(1, m+1):
        
        di = i*1.0
        z = math.cos(pi*(di - 0.25)/dnumPointsPlusHalf)
        zSq = z*z
        z1 = 0.0

        # Starting with the above approximation for the ith root,
        # we enter the main loop of refinement by Newton's method
        while (abs(z - z1) > weightsPrecision):
            p1 = 1.0
            p2 = 0.0
                
            # Calculate the Legendre polynomial at z using recurrence relation
            for j in range(1, numPoints+1):
                p3 = p2
                p2 = p1
                p1 = ((2.0*j - 1.0)*z*p2 - (j - 1.0)*p3)/(j*1.0)

	    # p1 = Legendre polynomial. Compute its derivative, pp
            pp = dnumPoints*(z*p1 - p2)/(zSq - 1.0)
            z1 = z
            z = z1 - (p1/pp) # Newton's method

	# Scale the root to the desired interval.
	# Vector entries start with 0, hence i-1 (where first i value is 1)
        abscissas[i-1] = z
        abscissas[numPoints-i] = abscissas[i-1] # Symmetric abscissa
        weights[i-1] = 2.0/((1.0 - zSq)*pp*pp)
        weights[numPoints-i] = weights[i-1] # Symmetric weight

    return (abscissas, weights)


def gauss2D(x, y, pars):

    # Normalised 2D Gaussian (total area = 1.0)
    argx = (x - pars.mux)/pars.sigmax
    argy = (y - pars.muy)/pars.sigmay
    gauss2D = (invTwoPi/(pars.sigmax*pars.sigmay))*math.exp(-0.5*(argx*argx + argy*argy))
    return gauss2D


def getGaussRPhiArea(gP, limits):

    (pointsR, weightsR) = calcGaussLegendreWeights(limits.nR)
    (pointsPhi, weightsPhi) = calcGaussLegendreWeights(limits.nPhi)

    # Scale the R grid points
    nR = int(limits.nR)
    midpoint = int((nR + 1)/2)
    for i in range(midpoint):

        ii = int(nR - 1 - i)
        dR = limits.halfRangeR*pointsR[i]
        rVal = limits.meanR - dR
        pointsR[i] = rVal
        rVal = limits.meanR + dR
        pointsR[ii] = rVal

    # Scale the phi grid points
    nPhi = int(limits.nPhi)
    midpoint = int((nPhi + 1)/2)
    for i in range(midpoint):

        ii = int(nPhi - 1 - i)
        dPhi = limits.halfRangePhi*pointsPhi[i]
        phiVal = limits.meanPhi - dPhi
        pointsPhi[i] = phiVal
        phiVal = limits.meanPhi + dPhi
        pointsPhi[ii] = phiVal

    # Get the integral over R and phi
    area = 0.0
    
    # R grid points
    for i in range(limits.nR):
        r = pointsR[i]

        # phi grid points
        for j in range(limits.nPhi):
            phi = pointsPhi[j]

            # 2D Gaussian
            x = r*math.cos(phi)
            y = r*math.sin(phi)
            fun = gauss2D(x, y, gP)

            # Integration weights * integration limits scaling * Jacobian
            # 2D area dx dy = r dr dphi, J = r
            weight = weightsR[i]*weightsPhi[j]*limits.intFactor*r

            # Add the area contribution
            area += weight*fun
            
    return area

    
def processArgs(parser):

    # Gaussian 2D area fraction & scraping option
    parser.add_argument('--frac', default=0.01, metavar='frac', type=float, help='Beam scraping fraction (0 to 1)')
    parser.add_argument('--option', default=1, metavar='option', type=int, help='Beam scraping option: 1 (sigma, default), 2 (offset)')


def run():

    # Process the command line arguments. Use "python getBaffleBeam.py --help" to see the full list
    parser = argparse.ArgumentParser(description='List of arguments')
    processArgs(parser)
    args = parser.parse_args()

    # Default beam
    mux0 = 0.0
    muy0 = 0.0
    sigma0 = 0.8/3
    sigmax0 = sigma0
    sigmay0 = sigma0

    gP = gaussPars(mux0, muy0, sigmax0, sigmay0, args.frac)
    allLimits = intRanges(0.0, 10.0, 1000, 0.0, twoPi, 1000)
    totArea = getGaussRPhiArea(gP, allLimits)

    minBaffleR = 1.335
    maxBaffleR = 7.60

    # Baffle front face boundary
    baffleLimits = intRanges(minBaffleR, maxBaffleR, 1000, 0.0, twoPi, 1000)

    if args.option == 1:

        # Case 1: vary sigma until we get the required area fraction (1%) on the baffle front face.
        # Use the bisection method to adjust sigma, comparing the fractional baffle areas
        print('Running bisectionSigma method for area fraction {0}'.format(gP.frac))
        minSigma = sigma0
        maxSigma = minBaffleR

        (meanSigma, meanDA) = bisectionSigma(minSigma, maxSigma, baffleLimits, gP)
        gP.sigmax = meanSigma
        gP.sigmay = meanSigma
        meanA = getGaussRPhiArea(gP, baffleLimits)
        print('*** meanSigma = {0:.6e} has meanDA = {1:.6e} & meanA = {2:.6e}'.format(meanSigma, meanDA, meanA))

    else:

        # Case 2: offset beam along x axis, but keep sigma = sigma0
        print('Running bisectionOffset method for area fraction {0}'.format(gP.frac))
        minOffset = 0.0
        # Set the maximum offset to be smaller than the maximum baffle radius,
        # since we need the overlapping baffle area to be large enough
        maxOffset = maxBaffleR*0.75
        (meanOffset, meanDA) = bisectionOffset(minOffset, maxOffset, baffleLimits, gP)
        gP.mux = meanOffset
        meanA = getGaussRPhiArea(gP, baffleLimits)
        print('*** meanOffset = {0:.6e} has meanDA = {1:.6e} & meanA = {2:.6e}'.format(meanOffset, meanDA, meanA))


def bisectionSigma(minSigma, maxSigma, baffleLimits, gP):

    gP.sigmax = minSigma
    gP.sigmay = minSigma
    minDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

    gP.sigmax = maxSigma
    gP.sigmay = maxSigma
    maxDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

    meanSigma = 0.0
    meanDA = 0.0

    if (minDA*maxDA > 0.0):
        print('minDA = {0:.6e} and maxDA = {1:.6e} have the same sign'.format(minDA, maxDA))
        return (meanSigma, meanDA)

    while ((maxSigma - minSigma) > gP.dSigma):

        meanSigma = 0.5*(minSigma + maxSigma)
        gP.sigmax = meanSigma
        gP.sigmay = meanSigma
        meanDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac
        if (abs(meanDA) < gP.epsilon):
            break

        # Decide which side is needed
        if (meanDA*minDA < 0.0):
            maxDA = meanDA
            maxSigma = meanSigma
        else:
            minDA = meanDA
            minSigma = meanSigma

        gP.sigmax = minSigma
        gP.sigmay = minSigma
        minDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

        gP.sigmax = maxSigma
        gP.sigmay = maxSigma
        maxDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

        print('minDA = {0:.6e} for minSigma = {1:.6e}, meanDA = {2:.6e} for meanSigma = {3:.6e}, ' \
              'maxDA = {4:.6e} for maxSigma = {5:.6e}'.format(minDA, minSigma, meanDA, meanSigma, maxDA, maxSigma))

    print('The required sigma is {0:.6e} for fractional area difference {1:.6e}'.format(meanSigma, meanDA))
    return (meanSigma, meanDA)


def bisectionOffset(minOffset, maxOffset, baffleLimits, gP):

    gP.mux = minOffset
    minDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

    gP.mux = maxOffset
    maxDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac
    print('Initial minOffset = {0:.6e}, minDA = {1:.6e}, maxOffset = {2:.6e}, maxDA = {3:.6e}'.format(minOffset,
                                                                                                      minDA,
                                                                                                      maxOffset,
                                                                                                      maxDA))
    
    meanOffset = 0.0
    meanDA = 0.0

    if (minDA*maxDA > 0.0):
        print('minDA = {0:.6e} and maxDA = {1:.6e} have the same sign'.format(minDA, maxDA))
        return (meanOffset, meanDA)

    while ((maxOffset - minOffset) > gP.dOffset):

        meanOffset = 0.5*(minOffset + maxOffset)
        gP.mux = meanOffset
        meanDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac
        if (abs(meanDA) < gP.epsilon):
            break

        # Decide which side is needed
        if (meanDA*minDA < 0.0):
            maxDA = meanDA
            maxOffset = meanOffset
        else:
            minDA = meanDA
            minOffset = meanOffset

        gP.mux = minOffset
        minDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

        gP.mux = maxOffset
        maxDA = getGaussRPhiArea(gP, baffleLimits) - gP.frac

        print('minDA = {0:.6e} for minOffset = {1:.6e}, meanDA = {2:.6e} for meanOffset = {3:.6e}, ' \
              'maxDA = {4:.6e} for maxOffset = {5:.6e}'.format(minDA, minOffset, meanDA, meanOffset,
                                                               maxDA, maxOffset))

    print('The required offset is {0:.6e} for fractional area difference {1:.6e}'.format(meanOffset, meanDA))
    return (meanOffset, meanDA)


if __name__ == '__main__':
    run()
