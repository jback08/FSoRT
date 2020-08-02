*$ CREATE MAGFLD.FOR
*COPY MAGFLD
*
*===magfld=============================================================*
*
      SUBROUTINE MAGFLD ( X, Y, Z, BTX, BTY, BTZ, B, NREG, IDISC )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
      INCLUDE '(CMEMFL)'
      INCLUDE '(CSMCRY)'
      INCLUDE 'fieldarray.inc'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1988-2005      by Alberto Fasso` & Alfredo Ferrari *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     Created  in 1988    by     Alberto Fasso`, CERN - TIS            *
*                                                                      *
*     Last change on 11-dec-92     by    Alfredo Ferrari               *
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
      COMMON/SOLMAP/FBX,FBY,FBZ,VOL
      
C     x,y,z volume limits
      DOUBLE PRECISION XL(2),YL(2),ZL(2)
C     dx, dy, dz values
      DOUBLE PRECISION DX,DY,DZ

C     X,Y,Z B field component arrays 
      DOUBLE PRECISION FBX(NX,NY,NZ)
      DOUBLE PRECISION FBY(NX,NY,NZ)
      DOUBLE PRECISION FBZ(NX,NY,NZ)
C     Storage of volume data
      DOUBLE PRECISION VOL(9)
C     Fractional local distance from start of bin co-ords
      DOUBLE PRECISION FRX,FRY,FRZ
C     Bin co-ordinate integers
      INTEGER IX,IY,IZ,INTARR(6)
C     Fractional bin distances
      DOUBLE PRECISION FRACD(6)
C     Needed to find B field components & directional cosines
      DOUBLE PRECISION BX,BY,BZ,BR,PHI

      LOGICAL FIRSTCALL
      DATA FIRSTCALL/.TRUE./
      SAVE FIRSTCALL !remember value of firstcall

      IF (FIRSTCALL) THEN
         CALL SUFI
         FIRSTCALL = .FALSE.
      ENDIF

C     Retrieve the volume limits
      XL(1) = VOL(1)
      YL(1) = VOL(2)
      ZL(1) = VOL(3)
      XL(2) = VOL(4)
      YL(2) = VOL(5)
      ZL(2) = VOL(6)
      DX    = VOL(7)
      DY    = VOL(8)
      DZ    = VOL(9)

C     Initialise the field components and magnitude
      BX = 0.0D0
      BY = 0.0D0
      BZ = 0.0D0

C      WRITE(*,*) 'MAGFLD COORD = ',X,Y,Z,XL(1),XL(2),YL(1),YL(2),
C     &                             ZL(1),ZL(2)

      IF (X.GE.XL(1).AND.X.LE.XL(2).AND.
     &    Y.GE.YL(1).AND.Y.LE.YL(2).AND.
     &    Z.GE.ZL(1).AND.Z.LE.ZL(2)) THEN

C        Get the bin numbers on either side of the (x,y,z) point.
C        Also calculate the fractional distance of the point from
C        the left and rightmost bins
         CALL GETFBIN(X,XL(1),DX,IX,FRX)
         CALL GETFBIN(Y,YL(1),DY,IY,FRY)
         CALL GETFBIN(Z,ZL(1),DZ,IZ,FRZ)

C         WRITE(*,*) 'IX,IY,IZ=',IX,IY,IZ

C        Do trilinear interpolation for each B field component.
C        This requires we find the values at the 8 "corners"
         IF (IX.GE.1.AND.IX.LT.NX.AND.
     &       IY.GE.1.AND.IY.LT.NY.AND.
     &       IZ.GE.1.AND.IZ.LT.NZ) THEN

            INTARR(1) = IX
            INTARR(2) = IY
            INTARR(3) = IZ
            INTARR(4) = IX + 1
            INTARR(5) = IY + 1
            INTARR(6) = IZ + 1

            FRACD(1) = FRX
            FRACD(2) = FRY
            FRACD(3) = FRZ
            FRACD(4) = 1.0D0 - FRX
            FRACD(5) = 1.0D0 - FRY
            FRACD(6) = 1.0D0 - FRZ

C           Calculate the field components using trilinear interpolation
            BX = TLINCALC(FBX,INTARR,FRACD)
            BY = TLINCALC(FBY,INTARR,FRACD)
            BZ = TLINCALC(FBZ,INTARR,FRACD)

C            WRITE(*,*) 'X,Y,Z = ',X,Y,Z,' B = ',BX,BY,BZ

         ENDIF

      ENDIF

C     Calculate the total field
      B = SQRT(BX*BX + BY*BY + BZ*BZ)
      IF (B.GT.1E-6) THEN
         BTX = BX/B
         BTY = BY/B
         BTZ = BZ/B
      ELSE
         BTX = 1.0D0
         BTY = 0.0D0
         BTZ = 0.0D0
      ENDIF
      
      IDISC = 0

      RETURN
      END    



      FUNCTION TLINCALC(FBX,INTARR,FRACD)
C     Function to calculate the field based on bilinear interpolation
      IMPLICIT NONE
C     Define the array storing the field map information (passed as an argument)
      INCLUDE 'fieldarray.inc'
      DOUBLE PRECISION FBX(NX,NY,NZ)
C     Define the array storing the bin numbers either side of the (x,y,z) point
      INTEGER INTARR(6)
      INTEGER IX,IX1,IY,IY1,IZ,IZ1
C     Define the returned field value and the fractional distance product array
      DOUBLE PRECISION TLINCALC, FRACD(6)
      DOUBLE PRECISION FRX,FRY,FRZ,FRX1,FRY1,FRZ1
      DOUBLE PRECISION VAL(6)

C     Get the bin numbers left and right of the point in (x,y,z)
      IX  = INTARR(1)
      IY  = INTARR(2)
      IZ  = INTARR(3)
      IX1 = INTARR(4)
      IY1 = INTARR(5)
      IZ1 = INTARR(6)
C     Fractional bin distances
      FRX = FRACD(1)
      FRY = FRACD(2)
      FRZ = FRACD(3)
C     1 - fractional bin distances
      FRX1 = FRACD(4)
      FRY1 = FRACD(5)
      FRZ1 = FRACD(6)

C     Do the trilinear interpolation
      VAL(1) = FBX(IX,IY,IZ)*FRX1   + FBX(IX1,IY,IZ)*FRX
      VAL(2) = FBX(IX,IY,IZ1)*FRX1  + FBX(IX1,IY,IZ1)*FRX
      VAL(3) = FBX(IX,IY1,IZ)*FRX1  + FBX(IX1,IY1,IZ)*FRX
      VAL(4) = FBX(IX,IY1,IZ1)*FRX1 + FBX(IX1,IY1,IZ1)*FRX

      VAL(5) = VAL(1)*FRY1 + VAL(3)*FRY
      VAL(6) = VAL(2)*FRY1 + VAL(4)*FRY

      TLINCALC = VAL(5)*FRZ1 + VAL(6)*FRZ

C      For debugging purposes
C      WRITE(*,*) 'BVal = ',TLINCALC,', I = ',IX,IY,IZ

      RETURN
      END



      SUBROUTINE GETFBIN(X,XMIN,DX,IX,FRX)
C     Get the bin for the given co-ordinate in the world volume
C     defined at the start of the field map file. Here "x" = x, y or z
      IMPLICIT NONE
      DOUBLE PRECISION X
      DOUBLE PRECISION XMIN, DX, DIST, FRX
      INTEGER IBIN, IX
C     Check whether we have a non-zero bin size
      IF (DX.GT.1E-10) THEN
C        Get the number of (fractional) bin widths the point is from
C        the first volume bin for the appropriate co-ordinate axis
         DIST = (X - XMIN)/DX
C        Get the integer equivalent of this distance
         IBIN = INT(DIST)
C        Get the actual fractional distance of the point from the
C        leftmost bin edge
         FRX = (DIST - IBIN*1.0)
         IX = IBIN + 1
      ELSE
         IX = 0
         FRX = 0.0D0
      ENDIF

C      WRITE(*,*) 'GETFBIN: ',X,IX,XMIN,DX,DIST,FRX

      RETURN
      END

C----------------------------------------------------
      SUBROUTINE SUFI
C................................................................
C     READS MAGNETIC FIELD MAP
      IMPLICIT DOUBLE PRECISION (A-H,O-Z), INTEGER (I-N)

C     Specify arrays storing B field data
      COMMON/SOLMAP/FBX,FBY,FBZ,VOL

C     x,y,z volume limits
      DOUBLE PRECISION XL(2),YL(2),ZL(2)
C     dx, dy, dz values
      DOUBLE PRECISION DX,DY,DZ

C     Need to use hard coded array sizes
      INCLUDE 'fieldarray.inc'
      DOUBLE PRECISION FBX(NX,NY,NZ)
      DOUBLE PRECISION FBY(NX,NY,NZ)
      DOUBLE PRECISION FBZ(NX,NY,NZ)
      DOUBLE PRECISION VOL(9)

      INTEGER NCX,NCY,NCZ
      INTEGER IX,IY,IZ,IERR

      DOUBLE PRECISION BX,BY,BZ

      WRITE(*,*) 'WITHIN SUFI CODE'

C     Open the field map file
      CALL OAUXFI('FieldMap3D.dat',LUNRDB,'OLD',IERR)
C     Store the volume dimensions and number of bins in the field map
      READ (LUNRDB,*) XL(1),YL(1),ZL(1),XL(2),YL(2),ZL(2),
     &                DX,DY,DZ,NCX,NCY,NCZ
      VOL(1) = XL(1)
      VOL(2) = YL(1)
      VOL(3) = ZL(1)
      VOL(4) = XL(2)
      VOL(5) = YL(2)
      VOL(6) = ZL(2)
      VOL(7) = DX
      VOL(8) = DY
      VOL(9) = DZ

C     Loop over the x,y,z bins and store the field component data.
C     Order the arrays such that the co-ords always increase
      N = 0
      DO IX = 1,NX,1
         DO IY = 1,NY,1
            DO IZ = 1,NZ,1
               READ (LUNRDB,*) X,Y,Z,BX,BY,BZ
               FBX(IX,IY,IZ) = BX
               FBY(IX,IY,IZ) = BY
               FBZ(IX,IY,IZ) = BZ
               N = N + 1
C               WRITE(*,*) 'Read: ',IX,IY,IZ,X,Y,Z,BX,BY,BZ
            ENDDO
         ENDDO
      ENDDO

      WRITE(*,*) 'NLines = ',N

      RETURN
      END
