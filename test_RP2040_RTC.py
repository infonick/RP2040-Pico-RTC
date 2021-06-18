# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
#
#    test_RP2040_RTC.py
#
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
#
# Tests for RP2040_RTC.py
#
# Requires:
#   - micropython-lib/python-stdlib/unittest/unittest.py from
#     https://github.com/micropython/micropython-lib/tree/master/python-stdlib/unittest
#   - RP2040-Pico-RTC/RP2040_RTC.py from
#     https://github.com/infonick/RP2040-Pico-RTC
#
# ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

from RP2040_RTC import rp2RTC
import unittest
import utime


class rp2RTC_Assertions_Group1(unittest.TestCase):    
    
    def test_rtc_running(self):
        self.assertIs(type(rp2RTC.rtc_running()), type(True))
    
    def test___validDateTime_Pass(self):
        for t in range(1577836800, 1640995200, 82739):
            (validYear, validMonth, validDay, validHour, validMinute, validSecond, _, _) = utime.localtime(t)
            self.assertTrue(rp2RTC.__validDateTime(validYear,
                                                   validMonth,
                                                   validDay,
                                                   validHour,
                                                   validMinute,
                                                   validSecond))
    
    
    def test_isLeapYear(self):
        for i in range(0,4096):
            
            if (i % 4) == 0:
               if (i % 100) == 0:
                   if (i % 400) == 0:
                       result = True
                   else:
                       result = False
               else:
                   result = True
            else:
               result = False
            
            self.assertEqual(rp2RTC.isLeapYear(i), result)
    
    
    def test_weekDay(self):
        for t in range(1577836800, 1640995200, 82739):
            (validYear, validMonth, validDay, _, _, _, DOTW, _) = utime.localtime(t)
            # Because Micropython uses a different DOTW number than the RP2040 RTC
            validDOTW = (DOTW+1)%7 
            self.assertEqual(rp2RTC.weekDay(validYear, validMonth, validDay), validDOTW)
    
    
    def test_localtime(self):
        (y, m, d, hr, mi, sc, dw, _) = utime.localtime()
        dw = (dw+1)%7 
        (year, month, day, hour, minute, second, dotw) = rp2RTC.localtime()
        
        self.assertEqual(year, y)
        self.assertEqual(month, m)
        self.assertEqual(day, d)
        self.assertEqual(hour, hr)
        self.assertEqual(minute, mi)
        self.assertEqual(second, sc)
        self.assertEqual(dotw, dw)
    


class rp2RTC_Assertions_Group2(unittest.TestCase):
    def setUp(self):
        self.validYear = 2020
        self.validMonth = 02
        self.validDay = 29
        self.validHour = 00
        self.validMinute = 00
        self.validSecond = 00
        
        self.invalidYear = set(range(-100,0,1)) | set(range(4096,4201,1))
        self.invalidMonth = set(range(-100,1,1)) | set(range(13,101,1))
        self.invalidDay = [set(range(-100,1,1)) | set(range(32,101,1)),
                           set(range(-100,1,1)) | set(range(30,101,1)),
                           set(range(-100,1,1)) | set(range(32,101,1)),
                           set(range(-100,1,1)) | set(range(31,101,1)),
                           set(range(-100,1,1)) | set(range(32,101,1)),
                           set(range(-100,1,1)) | set(range(31,101,1)),
                           set(range(-100,1,1)) | set(range(32,101,1)),
                           set(range(-100,1,1)) | set(range(32,101,1)),
                           set(range(-100,1,1)) | set(range(31,101,1)),
                           set(range(-100,1,1)) | set(range(32,101,1)),
                           set(range(-100,1,1)) | set(range(31,101,1)),
                           set(range(-100,1,1)) | set(range(32,101,1)),]
        self.invalidHour = set(range(-100,0,1)) | set(range(24,101,1))
        self.invalidMinute = set(range(-100,0,1)) | set(range(60,101,1))
        self.invalidSecond = set(range(-100,0,1)) | set(range(60,101,1))

        
    def test___validDateTime_FailYear(self):
        for i in self.invalidYear:
            with self.assertRaises(ValueError):
                rp2RTC.__validDateTime(i,
                                       self.validMonth,
                                       self.validDay,
                                       self.validHour,
                                       self.validMinute,
                                       self.validSecond)
    
    
    def test___validDateTime_FailMonth(self):
        for i in self.invalidMonth:
            with self.assertRaises(ValueError):
                rp2RTC.__validDateTime(self.validYear,
                                       i,
                                       self.validDay,
                                       self.validHour,
                                       self.validMinute,
                                       self.validSecond)
    
    
    def test___validDateTime_FailHour(self):
        for i in self.invalidHour:
            with self.assertRaises(ValueError):
                rp2RTC.__validDateTime(self.validYear,
                                       self.validMonth,
                                       self.validDay,
                                       i,
                                       self.validMinute,
                                       self.validSecond)


    def test___validDateTime_FailMinute(self):
        for i in self.invalidMinute:
            with self.assertRaises(ValueError):
                rp2RTC.__validDateTime(self.validYear,
                                       self.validMonth,
                                       self.validDay,
                                       self.validHour,
                                       i,
                                       self.validSecond)


    def test___validDateTime_FailSecond(self):
        for i in self.invalidSecond:
            with self.assertRaises(ValueError):
                rp2RTC.__validDateTime(self.validYear,
                                       self.validMonth,
                                       self.validDay,
                                       self.validHour,
                                       self.validMinute,
                                       i)


    def test___validDateTime_FailDay(self):        
        for m in range(1,13):
            for i in self.invalidDay[m-1]:
                with self.assertRaises(ValueError):
                    rp2RTC.__validDateTime(2020,
                                           m,
                                           i,
                                           self.validHour,
                                           self.validMinute,
                                           self.validSecond)
                    
                    
    def test___validDateTime_FailValueError(self):
        with self.assertRaises(ValueError):
            rp2RTC.__validDateTime(2021,
                                   2,
                                   29,
                                   self.validHour,
                                   self.validMinute,
                                   self.validSecond)


    def test___validDateTime_FailTypeErrorYear(self):
        with self.assertRaises(TypeError):
            rp2RTC.__validDateTime('self.validYear',
                                   self.validMonth,
                                   self.validDay,
                                   self.validHour,
                                   self.validMinute,
                                   self.validSecond)


    def test___validDateTime_FailTypeErrorMonth(self):
        with self.assertRaises(TypeError):
            rp2RTC.__validDateTime(self.validYear,
                                   'self.validMonth',
                                   self.validDay,
                                   self.validHour,
                                   self.validMinute,
                                   self.validSecond)


    def test___validDateTime_FailTypeErrorDay(self):
        with self.assertRaises(TypeError):
            rp2RTC.__validDateTime(self.validYear,
                                   self.validMonth,
                                   'self.validDay',
                                   self.validHour,
                                   self.validMinute,
                                   self.validSecond)


    def test___validDateTime_FailTypeErrorHour(self):
        with self.assertRaises(TypeError):
            rp2RTC.__validDateTime(self.validYear,
                                   self.validMonth,
                                   self.validDay,
                                   'self.validHour',
                                   self.validMinute,
                                   self.validSecond)


    def test___validDateTime_FailTypeErrorMinute(self):
        with self.assertRaises(TypeError):
            rp2RTC.__validDateTime(self.validYear,
                                   self.validMonth,
                                   self.validDay,
                                   self.validHour,
                                   'self.validMinute',
                                   self.validSecond)
            
            
    def test___validDateTime_FailTypeErrorSecond(self):
        with self.assertRaises(TypeError):
            rp2RTC.__validDateTime(self.validYear,
                                   self.validMonth,
                                   self.validDay,
                                   self.validHour,
                                   self.validMinute,
                                   'self.validSecond')
    


class rp2RTC_Assertions_Group3(unittest.TestCase):
    def test_setRTC(self):
        y = 2020
        m = 02
        d = 29
        hr = 23
        mi = 59
        sc = 59
        dw = 6
        
        (yearO, monthO, dayO, hourO, minuteO, secondO, dotwO) = rp2RTC.localtime()

        self.assertTrue(rp2RTC.setRTC(y, m, d, hr, mi, sc))
        (year, month, day, hour, minute, second, dotw) = rp2RTC.localtime()
        
        self.assertAlmostEqual(year, y, delta= 0)
        self.assertAlmostEqual(month, m, delta= 0)
        self.assertAlmostEqual(day, d, delta= 0)
        self.assertAlmostEqual(hour, hr, delta= 1)
        self.assertAlmostEqual(minute, mi, delta= 1)
        self.assertAlmostEqual(second, sc, delta= 1)
        self.assertAlmostEqual(dotw, dw, delta= 0)

        self.assertTrue(rp2RTC.setRTC(yearO, monthO, dayO, hourO, minuteO, secondO))
        (year, month, day, hour, minute, second, dotw) = rp2RTC.localtime()
        
        self.assertAlmostEqual(year, yearO, delta= 0)
        self.assertAlmostEqual(month, monthO, delta= 0)
        self.assertAlmostEqual(day, dayO, delta= 0)
        self.assertAlmostEqual(hour, hourO, delta= 1)
        self.assertAlmostEqual(minute, minuteO, delta= 1)
        self.assertAlmostEqual(second, secondO, delta= 1)
        self.assertAlmostEqual(dotw, dotwO, delta= 0)


if __name__ == "__main__":
    unittest.main()