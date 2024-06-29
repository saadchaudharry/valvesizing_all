import math
def findX(inletPressure, outletPressure):
    a = (inletPressure - outletPressure) / inletPressure
    return a


def findPvc(inletPressure, outletPressure, Flp, Fp):
    x = findX(inletPressure, outletPressure)
    a_ = x / ((Flp / Fp) ** 2)
    a = inletPressure * (1 - a_)
    return round(a, 1)

def findXvcc(gamma):
    a_ = (2 / (gamma + 1)) ** (gamma / (gamma - 1))
    a = 1 - a_
    return round(a, 3)

def findXC(gamma, Flp, Fp):
    xvcc = findXvcc(gamma)
    a_ = ((Flp / Fp) ** 2) * xvcc
    return round(a_, 3)

def alpha(gamma, Flp, Fp):
    xvcc = findXvcc(gamma)
    xc = findXC(gamma, Flp, Fp)
    a = (1 - xvcc) / (1 - xc)
    return round(a, 3)

def findXb(gamma, Flp, Fp):
    a_ = (1 / gamma) ** (gamma / (gamma - 1))
    al = alpha(gamma, Flp, Fp)
    b_ = (1 / al) * a_
    a = 1 - b_
    return round(a, 3)


def findXce(gamma, Flp, Fp):
    al = alpha(gamma, Flp, Fp)
    a = 1 - (1 / (22 * al))
    return round(a, 3)


def DJ(fd, C, Flp, Fp, N14):
    a_ = math.sqrt(C * (Flp / Fp))
    
    a = N14 * fd * a_
    return round(a, 3)

def DH(A, Iw):
    print(f'INSIDE DH {A},{Iw}')
    a = (4 * A) / Iw
    return round(a, 3)

def DO(A, No):
    a = (4 * No * A ) / math.pi
    return round(math.sqrt(a),3)

def FD(dh, do):
    a = dh / do
    return round(a,3)

def getRegime(inletPressure, outletPressure, gamma, Flp, Fp):
    x = findX(inletPressure, outletPressure)
    xc = findXC(gamma, Flp, Fp)
    xvcc = findXvcc(gamma)
    xb = findXb(gamma, Flp, Fp)
    xce = findXce(gamma, Flp, Fp)

    if x <= xc:
        return 'I'
    elif xc < x <= xvcc:
        return 'II'
    elif xvcc < x <= xb:
        return 'III'
    elif xb < x <= xce:
        return 'IV'
    elif xce < x:
        return 'V'

# regime 1 stream power of mass flow
def MVC_I(gamma, inletPressure, outletPressure, Flp, Fp):
    Fl = Flp / Fp
    a_ = 2 / (gamma - 1)
    x = findX(inletPressure, outletPressure)
    print(f'BEFORE b__ {x},{Fl}')
    b__ = 1 - (x / Fl ** 2)
    print(f'b__ {b__}')
    b_ = (b__ ** ((1 - gamma) / gamma)) - 1
    a = math.sqrt(a_ * b_)
    return round(a, 3)


def CVC_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi):
    x = findX(inletPressure, outletPressure)
    Fl = Flp / Fp
    b__ = (1 - (x / Fl ** 2)) ** ((gamma - 1) / gamma)
    c_ = gamma * inletPressure / Pi
    a = math.sqrt(c_ * b__)
    return round(a, 2)

def WM_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate):
    mvc = MVC_I(gamma, inletPressure, outletPressure, Flp, Fp)
    cvc = CVC_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi)
    a_ = (mvc * cvc) ** 2
    a = massflowrate * a_ / 2
    return round(a, 1)  


def TVC_I(gamma, inletPressure, outletPressure, Flp, Fp, inletTemp):
    x = findX(inletPressure, outletPressure)
    Fl = Flp / Fp
    b__ = (1 - (x / Fl ** 2)) ** ((gamma - 1) / gamma)
    a = inletTemp * b__
    return round(a, 1)

def eta_aef_I(gamma, inletPressure, outletPressure, Flp, Fp, aEta):
    a_ = 1 * (10 ** aEta)
    b_ = (Flp / Fp) ** 2
    mvc3 = MVC_I(gamma, inletPressure, outletPressure, Flp, Fp) ** 3
    # mvc3 = 0.988**3
    a = a_ * b_ * mvc3
    return round(a, 7)

def WA_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta):
    eta_ae = eta_aef_I(gamma, inletPressure, outletPressure, Flp, Fp, aEta)
    wm = WM_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate)
    a = eta_ae * wm
    return round(a, 1)

def peakFreq_fp_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C):
    fd = DH(A, Iw) / DO(A, No)
    dj = DJ(fd, C, Flp, Fp, 0.0046)
    mvc = MVC_I(gamma, inletPressure, outletPressure, Flp, Fp)
    cvc = CVC_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi)
    print(f'PEAK {fd}, {dj}, {mvc}, {cvc}')
    a = (stp * mvc * cvc )/ dj
    return a


# regime 2

def CVC_II(gamma, inletPressure, Pi):
    a_ = 2 * gamma * inletPressure / ((gamma + 1) * Pi)
    a = math.sqrt(a_)
    return round(a, 1)

def WM_II(gamma, inletPressure, Pi, massflowrate):
    cvcc = CVC_II(gamma, inletPressure, Pi)
    a = (massflowrate * cvcc * cvcc) / 2
    return round(a, 1)

def MJ_II(gamma, inletPressure, outletPressure, Flp, Fp):
    x = findX(inletPressure, outletPressure)
    al = alpha(gamma, Flp, Fp)
    a_1 = (2 / (gamma - 1)) * (((1 / (al * (1 - x))) ** ((gamma - 1) / gamma)) - 1)
    a1 = math.sqrt(a_1)
    a_2 = (2 / (gamma - 1)) * ((22 ** ((gamma - 1) / gamma)) - 1)
    a2 = math.sqrt(a_2)
    a = min(a1, a2)
    return round(a, 2)

def eta_aef_II(gamma, inletPressure, outletPressure, Flp, Fp, aEta):
    mj = MJ_II(gamma, inletPressure, outletPressure, Flp, Fp)
    x = findX(inletPressure, outletPressure)
    xvcc = findXvcc(gamma)
    power = 6.6 * ((Flp / Fp) ** 2)
    print(power)
    mj_p = mj ** power
    print(mj_p)
    a_ = 1 * (10 ** aEta)

    b_ = x / xvcc
    a = a_ * b_ * mj_p
    return round(a, 5)

def WA_II(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate):
    eta_aef = eta_aef_II(gamma, inletPressure, outletPressure, Flp, Fp, aEta)
    wm = WM_II(gamma, inletPressure, Pi, massflowrate)
    wa = eta_aef * wm
    return round(wa, 1)


def peakFreq_fp_II(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C):
    fd = DH(A, Iw) / DO(A, No)
    dj = DJ(fd, C, Flp, Fp, 0.0046)
    mj = MJ_II(gamma, inletPressure, outletPressure, Flp, Fp)
    cvc = CVC_II(gamma, inletPressure, Pi)
    a = stp * mj * cvc / dj
    return a


# regime 3
def eta_aef_III(gamma, inletPressure, outletPressure, Flp, Fp, aEta):
    mj = MJ_II(gamma, inletPressure, outletPressure, Flp, Fp)
    power = 6.6 * ((Flp / Fp) ** 2)
    # print(power)
    mj_p = mj ** power
    # print(mj_p)
    a_ = 1 * (10 ** aEta)
    # print(a_)
    a = a_ * mj_p
    return round(a, 5)

def WA_III(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate):
    eta_aef = eta_aef_III(gamma, inletPressure, outletPressure, Flp, Fp, aEta)
    wm = WM_II(gamma, inletPressure, Pi, massflowrate)
    wa = eta_aef * wm
    return round(wa, 1)

def peakFreq_fp_III(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C):
    fd = DH(A, Iw) / DO(A, No)
    dj = DJ(fd, C, Flp, Fp, 0.0046)
    mj = MJ_II(gamma, inletPressure, outletPressure, Flp, Fp)
    cvc = CVC_II(gamma, inletPressure, Pi)
    a = stp * mj * cvc / dj
    return a


# regime 4
def eta_aef_IV(gamma, inletPressure, outletPressure, Flp, Fp, aEta):
    mj = MJ_II(gamma, inletPressure, outletPressure, Flp, Fp)
    b_ = mj * mj / 2
    power = 6.6 * ((Flp / Fp) ** 2)
    # print(power)
    mj_p = math.sqrt(2) ** power
    # print(mj_p)
    a_ = 1 * (10 ** aEta)
    # print(a_)
    a = a_ * b_ * mj_p
    return round(a, 4)


def WA_IV(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate):
    eta_aef = eta_aef_IV(gamma, inletPressure, outletPressure, Flp, Fp, aEta)
    wm = WM_II(gamma, inletPressure, Pi, massflowrate)
    wa = eta_aef * wm
    return round(wa, 1)


# Peak Frequency
def peakFreq_fp_IV(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C):
    fd = DH(A, Iw) / DO(A, No)
    dj = DJ(fd, C, Flp, Fp, 0.0046)
    mj = MJ_II(gamma, inletPressure, outletPressure, Flp, Fp)
    cvc = CVC_II(gamma, inletPressure, Pi)
    a__ = 1.4 * stp * cvc
    b__ = dj * math.sqrt(mj * mj - 1)
    a = a__ / b__
    return round(a, 1)


def TVC_II(gamma, intemp):
    return (2 * intemp) / (gamma + 1)


# outlet density
def outDense(inletPressure, outletPressure, Pi):
    a = Pi * (outletPressure / inletPressure)
    return round(a, 2)

# speed of sound at downstream conditions
def C2(gamma, R, temp, M):
    a_ = gamma * R * temp / M
    a = math.sqrt(a_)
    return round(a)

#mach no at valve outlet
def MO(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, valveDia):
    print(f'MOOO {gamma},{inletPressure},{outletPressure},{Pi},{R},{temp},{M},{massflowrate},{valveDia}')
    p2 = outDense(inletPressure, outletPressure, Pi)
    c2 = C2(gamma, R, temp, M)
    # print(p2, c2)
    a_ = math.pi * valveDia * valveDia * p2 * c2
    a = 4 * massflowrate / a_
    print(f'MOFINALBEFORE {valveDia}, {p2} , {c2},{round(a,4)}')
    return round(a, 4)

def M2(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, Di):
   
    p2 = outDense(inletPressure, outletPressure, Pi)
    c2 = C2(gamma, R, temp, M)
    print(f'M2valuesss {p2}, {c2},{Di}')
    a_ = math.pi * Di * Di * p2 * c2
    print(f'a_I {a_},{massflowrate}')
    a = 4 * massflowrate / a_

    print(f'M2 {a},{round(a,4)}')
    return round(a, 4)


#correction for mach no
def LG(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, Di):
    # p2 = outletDensity(inletPressure, outletPressure, Pi)
    m2 = M2(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, Di)
    print(f'M2VALUES {m2}')

    a_ = 1 / (1 - m2)

    log__ = math.log10(a_)
    # log__ = numpy.log(a_)

    # print(f"a_ for m2: {round(a_, 4)}, {log__}")
    a = 16 * log__
    return round(a, 2)

# overall internal sound-pressure level
def LPI(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia, internalPipeDia):
    regime_no = getRegime(inletPressure, outletPressure, gamma, Flp, Fp)
    if regime_no == 'I':
        wa = WA_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta)
    elif regime_no == 'II':
        wa = WA_II(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate)
    elif regime_no == 'III':
        wa = WA_III(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate)
    elif regime_no == 'IV':
        wa = WA_IV(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate)
    elif regime_no == 'V':
        wa = WA_IV(gamma, inletPressure, outletPressure, Flp, Fp, aEta, Pi, massflowrate)

    print(f'INSIDE LPI {wa}')

    p2 = outDense(inletPressure, outletPressure, Pi)
    c2 = C2(gamma, R, temp, M)  
   
    lg = LG(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, internalPipeDia)
    # print(f"Wa: {wa}, p2: {p2}, c2: {c2}, dj: , lg: {lg}")

    a__ = (3.2 * (10 ** 9)) * wa * p2 * c2 / (internalPipeDia ** 2)
    print(f'PJSJSJJ {p2},{wa},{c2},{internalPipeDia},{lg}')
    a_ = 10 * math.log10(a__)
    a = a_ + lg
    return round(a, 1)


# ring frequency
def fr(cs, internalPipeDia):
    a = cs / (math.pi * internalPipeDia)
    return round(a)


# internal coincidence pipe frequency
def fo(gamma, R, temp, M, cs, internalPipeDia, ca):
    c2 = C2(gamma, R, temp, M)
    f_r = fr(cs, internalPipeDia)
    a = f_r * c2 / (4 * ca)
    return round(a)


# external coincidence frequency
def fg(ca, cs, ts):
    a = math.sqrt(3) * ca * ca / (math.pi * ts * cs)
    return round(a)


# frequencies
frequencies = [12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250,
               1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]

a_factor = [-63.4, -56.7, -50.5, -44.7, -39.4, -34.6, -30.2, -26.2, 22.5, -19.1, -16.1, -13.4, -10.9, -8.6, -6.6, -4.8,
            -3.2, -1.9, -0.8, 0, 0.6, 1, 1.2, 1.3, 1.2, 1, 0.5, -0.1, -1.1, -2.5, -4.3, -6.6, -9.3]

freq_dict_list = []

for i in range(len(frequencies)):
    a_dict = {'fr': frequencies[i], 'del_l': a_factor[i]}
    freq_dict_list.append(a_dict)

# Frequency dependent internal spl (3rd octave bands: 12.5hz - 20 khz)
def L_pi_fi(fi, gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
            internalPipeDia, stp, No, A, Iw, C):
    regime_no = getRegime(inletPressure, outletPressure, gamma, Flp, Fp)
    if regime_no == 'I':
        fp = peakFreq_fp_I(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C)
    elif regime_no == 'II':
        fp = peakFreq_fp_II(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C)
    elif regime_no == 'III':
        fp = peakFreq_fp_III(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C)
    elif regime_no == 'IV' or regime_no == 'V':
        fp = peakFreq_fp_IV(gamma, inletPressure, outletPressure, Flp, Fp, Pi, stp, No, A, Iw, C)





    a__ = 1 + ((fi / (2 * fp)) ** 2.5)
    b__ = 1 + ((fp / (2 * fi)) ** 1.7)
    a_ = a__ * b__
    lpi = LPI(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
              internalPipeDia)
    a = lpi - 8 - 10 * math.log10(a_)
    print(f"NOISE LPIFI {a}")
    return a


# combined internal spl at pipe wall, caused by valve trim and expander
def lpi_s_fi(fi, gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
             internalPipeDia, stp, No, A, Iw, C, valveDia, aeta):
    lpi_fi_ = L_pi_fi(fi, gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
                      internalPipeDia, stp, No, A, Iw, C)
    lpi_r__fi = lpi_r_fi(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia,
                         aeta,
                         oPipeDia, stp, fi)
    a__ = 10 ** (lpi_fi_ / 10) + 10 ** (lpi_r__fi / 10)
    a = 10 * math.log10(a__)
    return a


# TODO - if MO is greater than 0.3, do the following formulae - 34-43 - only for Case 6 in testing
# Gas velocity in downstream pipe
def UP(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M):
    p2 = outDense(inletPressure, outletPressure, Pi)
    c2 = C2(gamma, R, temp, M)
    # print(f"p2, c2: {p2}, {c2}")
    a = 4 * massflowrate / (math.pi * p2 * internalPipeDia * internalPipeDia)
    # print(f"numerator: {4 * massflowrate}, denominator: {(math.pi * p2 * internalPipeDia * internalPipeDia)}")
    if a <= 0.8 * c2:
        # print('UP is less than 0.8*c2')
        pass
    else:
        # print('UP is not less than 0.8*c2')
        pass
    return a

# Gas velocity in the inlet of diameter expander
def UR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia):
    up = UP(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M)
    a_ = up * internalPipeDia * internalPipeDia / (0.93 * valveDia * valveDia)
    c2 = C2(gamma, R, temp, M)
    if a_ <= c2:
        # print('UR is less than c2')
        pass
    else:
        pass
        # print('UR is not less than c2')
    return a_


# peak frequency in valve outlet or reduced dia of expander
def fpr(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, stp):
    ur = UR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia)
    a = stp * ur / valveDia
    return a

# frequency dependent internal spl at pipe wall for noise created by outlet flow in expander
def lpi_r_fi(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta,
             oPipeDia, stp, fi):
    lpir = lpi_r(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta,
                 oPipeDia)
    fp__r = fpr(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, stp)
    a__ = ((fi / (2 * fp__r)) ** 2.5) + 1
    b__ = ((fp__r / (2 * fi)) ** 1.7) + 1
    a_ = a__ * b__
    a = lpir - 8 - 10 * math.log10(a_)
    return a



# mach number at the entranc eto expander
def MR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia):
    ur = UR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia)
    c2 = C2(gamma, R, temp, M)
    a = ur / c2
    return round(a, 3)



# acoustical efficiency factor for noise created by outlet flow in expander
def etaR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta):
    mr = MR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia)
    a__ = (10 ** aeta) * (mr ** 3)
    return a__


# converted stream power in the expander
def WMR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia):
    ur = UR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia)
    a__ = massflowrate * ur * ur / 2
    b__ = ((1 - (valveDia ** 2 / internalPipeDia ** 2)) ** 2) + 0.2
    a = a__ * b__
    return a

# sound power for nosie generated by output flow
def WAR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta):
    eta_r = etaR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta)
    wmr = WMR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia)
    a = eta_r * wmr
    return a

# overall internal sound-pressure level at pipe wall for noise created by outlet flow in expander
def lpi_r(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta,
          oPipeDia):
    p2 = outDense(inletPressure, outletPressure, Pi)
    c2 = C2(gamma, R, temp, M)
    lg = LG(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, oPipeDia)
    # print(f"lg: {lg}")
    war = WAR(gamma, inletPressure, outletPressure, Pi, massflowrate, internalPipeDia, R, temp, M, valveDia, aeta)
    a__ = (3.2 * (10 ** 9)) * war * p2 * c2 / (internalPipeDia ** 2)
    a_ = 10 * math.log10(a__) + lg
    return a_


# damping factor for transmission loss
def del_TL(valveDia):
    a = -16660 * (valveDia ** 3) + 6370 * (valveDia ** 2) - 813 * valveDia + 35.8
    if valveDia > 0.15:
        return 0
    elif 0.05 <= valveDia <= 0.15:
        return round(a, 1)
    elif valveDia < 0.05:
        return 9



# frequency factor Gx
def GX_fi(gamma, R, temp, M, cs, internalPipeDia, ca, fi):
    f_O = fo(gamma, R, temp, M, cs, internalPipeDia, ca)
    f_r = fr(cs, internalPipeDia)

    if fi < f_O:
        a_ = (f_O / f_r) ** (2 / 3)
        b_ = (fi / f_O) ** 4
        a = a_ * b_
        return a
    elif f_O <= fi < f_r:
        a = (fi / f_r) ** (1 / 2)
        return a
    elif (fi >= f_O) and (fi >= f_r):
        a = 1
        return a
    
# Frequency factor Gy
def GY_fi(gamma, R, temp, M, cs, internalPipeDia, ca, ts, fi):
    f_o = fo(gamma, R, temp, M, cs, internalPipeDia, ca)
    f_g = fg(ca, cs, ts)

    if fi < f_o < f_g:
        a = f_o / f_g
        return a
    elif fi < f_o and f_o >= f_g:
        return 1
    elif f_o <= fi < f_g:
        a = fi / f_g
        return a
    elif fi >= f_o and fi >= f_g:
        return 1

# frequency dependent structural loss factor

def eta_S_fi(fs, fi):
    # Structural loss factor reference frequency = 1 Hz - fs
    a = math.sqrt(fs / (fi * 100))
    return round(a, 5)

# Frequency dependent transmission loss
def TL_fi(gamma, inletPressure, outletPressure, Pi, R, temp, M, cs, internalPipeDia, ca, valveDia, ts, fs, fi, pa, ps,
          rho_s):
    c2 = C2(gamma, R, temp, M)
    eta_s = eta_S_fi(fs, fi)
    p2 = outDense(inletPressure, outletPressure, Pi)
    gyfi = GY_fi(gamma, R, temp, M, cs, internalPipeDia, ca, ts, fi)
    gxfi = GX_fi(gamma, R, temp, M, cs, internalPipeDia, ca, fi)
    d_tl = del_TL(valveDia)
    denom = ((p2 * c2 + 2 * math.pi * ts * fi * rho_s * eta_s) / (415 * gyfi)) + 1
    numer = (8.25 * (10 ** (-7))) * ((c2 / (ts * fi)) ** 2) * gxfi
    pres_factor = pa / ps
    a_ = numer * pres_factor / denom
    a = 10 * math.log10(a_) - d_tl
    return round(a, 1)

def lpe_1m_fi(fi, gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
              internalPipeDia, stp, No, A, Iw, C, cs, ca, valveDia, ts, fs, pa, ps, rho_s, aeta):


    tl_fi = TL_fi(gamma, inletPressure, outletPressure, Pi, R, temp, M, cs, internalPipeDia, ca, valveDia, ts, fs, fi,
                  pa, ps, rho_s)

    a_ = (internalPipeDia + 2 * ts + 2) / (internalPipeDia + 2 * ts)
    a__ = 10 * math.log10(a_)
    mo = MO(gamma, inletPressure, outletPressure, Pi, R, temp, M, massflowrate, oPipeDia)
    print(f'MOLPAEM {mo}')
    if mo > 0.3:
        lpi_s__fi = lpi_s_fi(fi, gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M,
                        oPipeDia,
                        internalPipeDia, stp, No, A, Iw, C, valveDia, aeta)

        lp = lpi_s__fi
    else:
        lpi_fi = L_pi_fi(fi, gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
                    internalPipeDia, stp, No, A, Iw, C)
        lp = lpi_fi
    a = lp + tl_fi - a__
    return a

def lpae_1m(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
            internalPipeDia, stp, No, A, Iw, C, cs, ca, valveDia, ts, fs, pa, ps, rho_s, aeta):
    print(gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp, M, oPipeDia,
            internalPipeDia, stp, No, A, Iw, C, cs, ca, valveDia, ts, fs, pa, ps, rho_s, aeta)
    sum__ = 0

    for dict__ in freq_dict_list:
        lpe_1m = lpe_1m_fi(dict__['fr'], gamma, inletPressure, outletPressure, Flp, Fp, Pi, massflowrate, aEta, R, temp,
                           M, oPipeDia,
                           internalPipeDia, stp, No, A, Iw, C, cs, ca, valveDia, ts, fs, pa, ps, rho_s, aeta)
        a = (lpe_1m + dict__['del_l']) / 10
        b = 10 ** a
        sum__ += b
        

    output = 10 * math.log10(sum__)
    print(f"output: {output}, sum: {sum__}, log: {math.log10(sum__)}")
    return output