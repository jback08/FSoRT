*                                                                      *
*=== mgdraw ===========================================================*
*                                                                      *
      SUBROUTINE MGDRAW ( ICODE, MREG )

      INCLUDE 'dblprc.inc'
      INCLUDE 'dimpar.inc'
      INCLUDE 'iounit.inc'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 2022: CERN                                         *
*     All Rights Reserved.                                             *
*                                                                      *
*     MaGnetic field trajectory DRAWing: actually this entry manages   *
*                                        all trajectory dumping for    *
*                                        drawing                       *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE 'caslim.inc'
      INCLUDE 'comput.inc'
      INCLUDE 'sourcm.inc'
      INCLUDE 'fheavy.inc'
      INCLUDE 'flkstk.inc'
      INCLUDE 'genstk.inc'
      INCLUDE 'mgddcm.inc'
      INCLUDE 'paprop.inc'
      INCLUDE 'quemgd.inc'
      INCLUDE 'sumcou.inc'
      INCLUDE 'trackr.inc'
*
      LOGICAL LFIRST
      INTEGER BAF1, BAF2, TPT1, TPT2, END1, END2
      SAVE LFIRST, BAF1, BAF2, TPT1, TPT2, END1, END2
      DATA LFIRST / .TRUE. /
*
*----------------------------------------------------------------------*
*                                                                      *
*     Icode = 1: call from Kaskad                                      *
*     Icode = 2: call from Emfsco                                      *
*     Icode = 3: call from Kasneu                                      *
*     Icode = 4: call from Kashea                                      *
*     Icode = 5: call from Kasoph                                      *
*                                                                      *
*----------------------------------------------------------------------*
*                                                                      *
      RETURN
*
*======================================================================*
*                                                                      *
*     Boundary-(X)crossing DRAWing:                                    *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             19: boundary crossing                                    *
*     Icode = 2x: call from Emfsco                                     *
*             29: boundary crossing                                    *
*     Icode = 3x: call from Kasneu                                     *
*             39: boundary crossing                                    *
*     Icode = 4x: call from Kashea                                     *
*             49: boundary crossing                                    *
*     Icode = 5x: call from Kasoph                                     *
*             59: boundary crossing                                    *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY BXDRAW ( ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO )
      IF ( LFIRST ) THEN
*     User initialization
         LFIRST = .FALSE.
*     Get the respective region numbers (only done once)
         BAF1 = 0
         BAF2 = 0
         TPT1 = 0
         TPT2 = 0
         END1 = 0
         END2 = 0
         CALL GEON2R('MBGASF1 ', BAF1, IERR1)
         CALL GEON2R('MBGASF2 ', BAF2, IERR1)
         CALL GEON2R('MBGASG  ', TPT1, IERR1)
         CALL GEON2R('MNTGAS1 ', TPT2, IERR1)
         CALL GEON2R('ENDGAS1 ', END1, IERR1)
         CALL GEON2R('ENDGAS2 ', END2, IERR1)
*     Open output file
         OPEN(UNIT = 99, FILE = 'data.txt', STATUS = 'new')
      END IF
*     Find particles crossing various regions
      IF ((MREG.EQ.BAF1.AND.NEWREG.EQ.BAF2).OR.
     &    (MREG.EQ.BAF2.AND.NEWREG.EQ.BAF1).OR.
     &    (MREG.EQ.TPT1.AND.NEWREG.EQ.TPT2).OR.
     &    (MREG.EQ.TPT2.AND.NEWREG.EQ.TPT1).OR.
     &    (MREG.EQ.END1.AND.NEWREG.EQ.END2).OR.
     &    (MREG.EQ.END2.AND.NEWREG.EQ.END1)) THEN
*     Only consider p, n, pi, mu, K particles (charged & neutral)
       IF (JTRACK.EQ.1.OR.JTRACK.EQ.8.OR.
     &     (JTRACK.GE.10.AND.JTRACK.LE.16).OR.JTRACK.EQ.19.OR.
     &     (JTRACK.GE.23.AND.JTRACK.LE.25)) THEN
*     Write out variables to file unit 99 (formatted as line 102)
            WRITE(99,102) NCASE,JTRACK,ETRACK,ETRACK-AM(JTRACK),
     &      WTRACK,XSCO,YSCO,ZSCO,CXTRCK,CYTRCK,CZTRCK,ATRACK
 102        FORMAT(I11,I7,6(1PE13.5),3(1PE15.7),1PE12.4)
        ENDIF
      ENDIF
      RETURN
*
*======================================================================*
*                                                                      *
*     Event End DRAWing:                                               *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY EEDRAW ( ICODE )
      RETURN
*
*======================================================================*
*                                                                      *
*     ENergy deposition DRAWing:                                       *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             10: elastic interaction recoil                           *
*             11: inelastic interaction recoil                         *
*             12: stopping particle                                    *
*             13: pseudo-neutron deposition                            *
*             14: escape                                               *
*             15: time kill                                            *
*             16: recoil from (heavy) bremsstrahlung                   *
*     Icode = 2x: call from Emfsco                                     *
*             20: local energy deposition (i.e. photoelectric)         *
*             21: below threshold, iarg=1                              *
*             22: below threshold, iarg=2                              *
*             23: escape                                               *
*             24: time kill                                            *
*     Icode = 3x: call from Kasneu                                     *
*             30: target recoil                                        *
*             31: below threshold                                      *
*             32: escape                                               *
*             33: time kill                                            *
*     Icode = 4x: call from Kashea                                     *
*             40: escape                                               *
*             41: time kill                                            *
*             42: delta ray stack overflow                             *
*     Icode = 5x: call from Kasoph                                     *
*             50: optical photon absorption                            *
*             51: escape                                               *
*             52: time kill                                            *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY ENDRAW ( ICODE, MREG, RULL, XSCO, YSCO, ZSCO )
      RETURN
*
*======================================================================*
*                                                                      *
*     SOurce particle DRAWing:                                         *
*                                                                      *
*======================================================================*
*
      ENTRY SODRAW
      RETURN
*
*======================================================================*
*                                                                      *
*     USer dependent DRAWing:                                          *
*                                                                      *
*     Icode = 10x: call from Kaskad                                    *
*             100: elastic   interaction secondaries                   *
*             101: inelastic interaction secondaries                   *
*             102: particle decay  secondaries                         *
*             103: delta ray  generation secondaries                   *
*             104: pair production secondaries                         *
*             105: bremsstrahlung  secondaries                         *
*             110: radioactive decay products                          *
*     Icode = 20x: call from Emfsco                                    *
*             208: bremsstrahlung secondaries                          *
*             210: Moller secondaries                                  *
*             212: Bhabha secondaries                                  *
*             214: in-flight annihilation secondaries                  *
*             215: annihilation at rest   secondaries                  *
*             217: pair production        secondaries                  *
*             219: Compton scattering     secondaries                  *
*             221: photoelectric          secondaries                  *
*             225: Rayleigh scattering    secondaries                  *
*             237: mu pair production     secondaries                  *
*     Icode = 30x: call from Kasneu                                    *
*             300: interaction secondaries                             *
*     Icode = 40x: call from Kashea                                    *
*             400: delta ray  generation secondaries                   *
*     Icode = 50x: call from synstp                                    *
*             500: synchrotron radiation photons from e-/e+            *
*             501: synchrotron radiation photons from other charged    *
*                  particles                                           *
*  For all interactions secondaries are put on GENSTK common (kp=1,np) *
*  but for KASHEA delta ray generation where only the secondary elec-  *
*  tron is present and stacked on FLKSTK common for kp=npflka          *
*                                                                      *
*======================================================================*
*
      ENTRY USDRAW ( ICODE, MREG, XSCO, YSCO, ZSCO )
      RETURN
*=== End of subrutine Mgdraw ==========================================*
      END

