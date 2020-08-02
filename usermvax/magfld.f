*$ CREATE MAGFLD.FOR
*COPY MAGFLD
*
*===magfld=============================================================*
*
      SUBROUTINE MAGFLD ( X, Y, Z, BTX, BTY, BTZ, B, NREG, IDISC )

      INCLUDE '(DBLPRU)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1988-2020      by Alberto Fasso` & Alfredo Ferrari *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     Created  in     1988         by    Alberto Fasso`                *
*                                                                      *
*                                                                      *
*     Last change on  10-Mar-20    by    Alberto Fasso`                *
*                                          SLAC/USA                    *
*                                                                      *
*     Input variables:                                                 *
*            x,y,z = current position                                  *
*            nreg  = current region                                    *
*     Output variables:                                                *
*            btx,bty,btz = cosines of the magn. field vector           *
*            B = magnetic field intensity (Tesla)                      *
*            idisc = set to 1 if the particle has to be discarded      *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(BLNKCM)'
      INCLUDE '(CMEMFL)'
      INCLUDE '(TRACKR)'
      INCLUDE '(CSMCRY)'

*     B = 0.02T*[I(kA)/r(cm)], I = 293
      COMMON/BPARS/ICURR,BDIR

      DOUBLE PRECISION BX,BY,BZ
      DOUBLE PRECISION ICURR,BDIR,R,PHI

*     Get field direction from input parameter file
      LOGICAL FIRSTCALL
      DATA FIRSTCALL/.TRUE./
      SAVE FIRSTCALL ! remember value of FIRSTCALL
      IF (FIRSTCALL) THEN
         CALL SUFI
         FIRSTCALL = .FALSE.
      ENDIF

*     Set field magnitude using B = I/R formula
      B = 0.0D0
      R = SQRT(X*X + Y*Y)
      IF (R.GT.0.0) THEN
         B = 0.02D0*ICURR/R
      ENDIF

*     Directional cosines depend on the horn current direction.
*     Neutrino running (+1): anticlockwise in x-y plane
*     Antineutrino running (-1): clockwise in x-y plane
*     Coordinate angle in x-y plane
      PHI = ATAN2(Y, X)

*     Get the field components
      BX = -1.0*BDIR*B*SIN(PHI)
      BY = BDIR*B*COS(PHI)
      BZ = 0.0D0
*     Set the field magnitude
      B = SQRT(BX*BX + BY*BY + BZ*BZ)

*     Finally set the field directional cosines
      IF (B.GT.1E-6) THEN
         BTX = BX/B
         BTY = BY/B
         BTZ = BZ/B
      ELSE
         BTX = 1.0D0
         BTY = 0.0D0
         BTZ = 0.0D0
      ENDIF

*     Keep the particle
      IDISC = 0
      
      RETURN
      END
      

      SUBROUTINE SUFI
*     Read parameter file to get field direction
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER (I-N)

      COMMON/BPARS/ICURR,BDIR

      DOUBLE PRECISION ICURR,BDIR
*     Open parameter file: current (kA) and direction (1 or -1)
      CALL OAUXFI('FieldPars.dat',LUNRDB,'OLD',IERR)
      READ (LUNRDB,*) ICURR,BDIR
      WRITE (*,*) 'Horn I = ',ICURR,'kA, dir = ',BDIR

      RETURN
      END
      
