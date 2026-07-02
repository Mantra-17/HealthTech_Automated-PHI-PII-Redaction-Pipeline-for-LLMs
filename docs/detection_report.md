# PHI Redaction Detection Report

This report documents the detailed numbers, categories, and positions of all Protected Health Information (PHI) entities detected across the 20 clinical notes.

## 1. High-Level Summary Metrics

* **Total Notes Scanned:** 20
* **Total PHI Ground Truth Items:** 246
* **Total Entities Detected:** 232
* **True Positives (TP):** 226
* **False Positives (FP):** 6
* **False Negatives (FN):** 20
* **Global Precision:** 97.41%
* **Global Recall:** 91.87%
* **Global F1-Score:** 94.56%

## 2. Global Entity Class Frequencies

| Entity Category | Count Detected | Description / Mapped Types |
| :--- | :---: | :--- |
| **PERSON** | 53 | Mapped to de-identification pipeline standard |
| **DATE** | 35 | Mapped to de-identification pipeline standard |
| **PHONE** | 21 | Mapped to de-identification pipeline standard |
| **EMAIL** | 17 | Mapped to de-identification pipeline standard |
| **US_DRIVER_LICENSE** | 16 | Mapped to de-identification pipeline standard |
| **MRN** | 15 | Mapped to de-identification pipeline standard |
| **LOCATION** | 15 | Mapped to de-identification pipeline standard |
| **ORGANIZATION** | 11 | Mapped to de-identification pipeline standard |
| **DATE_TIME** | 9 | Mapped to de-identification pipeline standard |
| **SSN** | 8 | Mapped to de-identification pipeline standard |
| **URL** | 8 | Mapped to de-identification pipeline standard |
| **AADHAAR** | 7 | Mapped to de-identification pipeline standard |
| **IP** | 6 | Mapped to de-identification pipeline standard |
| **PHONE_NUMBER** | 6 | Mapped to de-identification pipeline standard |
| **US_SSN** | 2 | Mapped to de-identification pipeline standard |
| **ZIP** | 1 | Mapped to de-identification pipeline standard |
| **INSURANCE** | 1 | Mapped to de-identification pipeline standard |
| **LICENSE** | 1 | Mapped to de-identification pipeline standard |

## 3. Per-Note Summary Statistics

| Note ID | Word Count | PHI Ground Truth | Detected | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| NOTE_001 | 52 | 15 | 15 | 15 | 0 | 0 | 100.00% |
| NOTE_002 | 47 | 15 | 15 | 15 | 0 | 0 | 100.00% |
| NOTE_003 | 45 | 12 | 10 | 10 | 0 | 2 | 83.33% |
| NOTE_004 | 45 | 12 | 11 | 11 | 0 | 1 | 91.67% |
| NOTE_005 | 52 | 15 | 13 | 13 | 0 | 2 | 86.67% |
| NOTE_006 | 52 | 14 | 13 | 13 | 0 | 1 | 92.86% |
| NOTE_007 | 47 | 13 | 11 | 11 | 0 | 2 | 84.62% |
| NOTE_008 | 47 | 14 | 12 | 12 | 0 | 2 | 85.71% |
| NOTE_009 | 46 | 11 | 11 | 11 | 0 | 0 | 100.00% |
| NOTE_010 | 44 | 15 | 14 | 14 | 0 | 1 | 93.33% |
| NOTE_011 | 50 | 14 | 12 | 12 | 0 | 2 | 85.71% |
| NOTE_012 | 52 | 15 | 14 | 14 | 0 | 1 | 93.33% |
| NOTE_013 | 44 | 15 | 13 | 13 | 0 | 2 | 86.67% |
| NOTE_014 | 53 | 14 | 13 | 13 | 0 | 1 | 92.86% |
| NOTE_015 | 48 | 14 | 14 | 14 | 0 | 0 | 100.00% |
| NOTE_016 | 56 | 12 | 11 | 11 | 1 | 1 | 91.67% |
| NOTE_017 | 50 | 7 | 8 | 6 | 2 | 1 | 85.71% |
| NOTE_018 | 48 | 9 | 9 | 8 | 1 | 1 | 88.89% |
| NOTE_019 | 40 | 6 | 8 | 6 | 1 | 0 | 100.00% |
| NOTE_020 | 42 | 4 | 5 | 4 | 1 | 0 | 100.00% |

## 4. Itemized Detections (All Notes)

| Note ID | Entity Category | Detected Text Value | Character Span (Start-End) |
| :--- | :--- | :--- | :---: |
| NOTE_001 | **PERSON** | `Rahul Sharma` | 8-20 |
| NOTE_001 | **DATE** | `14/02/1985` | 27-37 |
| NOTE_001 | **DATE** | `05/06/2026` | 50-60 |
| NOTE_001 | **MRN** | `MRN-00234` | 88-97 |
| NOTE_001 | **US_DRIVER_LICENSE** | `9876543210` | 108-118 |
| NOTE_001 | **PHONE** | `+91-98765-43210` | 130-145 |
| NOTE_001 | **EMAIL** | `rahul.sharma@gmail.com` | 154-176 |
| NOTE_001 | **AADHAAR** | `1234 5678 9012` | 187-201 |
| NOTE_001 | **LOCATION** | `MG Road` | 215-222 |
| NOTE_001 | **LOCATION** | `Mumbai` | 224-230 |
| NOTE_001 | **US_DRIVER_LICENSE** | `400001` | 231-237 |
| NOTE_001 | **IP** | `192.168.1.1` | 262-273 |
| NOTE_001 | **PERSON** | `Emily Carter` | 287-299 |
| NOTE_001 | **PERSON** | `Arjun Mehta` | 320-331 |
| NOTE_001 | **DATE** | `June 9 2026` | 349-360 |
| NOTE_002 | **PERSON** | `Sarah Johnson` | 9-22 |
| NOTE_002 | **DATE** | `1989-11-23` | 28-38 |
| NOTE_002 | **PHONE_NUMBER** | `06-14-2026` | 54-64 |
| NOTE_002 | **PHONE** | `(312) 555-7812` | 96-110 |
| NOTE_002 | **PHONE** | `312-555-9910` | 123-135 |
| NOTE_002 | **EMAIL** | `sarah.johnson@northvalley.org` | 143-172 |
| NOTE_002 | **SSN** | `421-66-9034` | 179-190 |
| NOTE_002 | **MRN** | `MRN-88321` | 197-206 |
| NOTE_002 | **ORGANIZATION** | `W Pine Ave` | 219-229 |
| NOTE_002 | **LOCATION** | `Chicago` | 231-238 |
| NOTE_002 | **LOCATION** | `IL 60614-2210` | 240-253 |
| NOTE_002 | **URL** | `https://northvalleyclinic.org/followup.` | 270-309 |
| NOTE_002 | **PERSON** | `Michael Brown` | 327-340 |
| NOTE_002 | **PERSON** | `Sarah Johnson` | 350-363 |
| NOTE_002 | **DATE** | `06/20/2026` | 388-398 |
| NOTE_003 | **PERSON** | `Vikram Iyer` | 6-17 |
| NOTE_003 | **PHONE_NUMBER** | `03-07-2026` | 36-46 |
| NOTE_003 | **DATE** | `2026-07-15` | 60-70 |
| NOTE_003 | **PHONE** | `+91 91234 56789` | 166-181 |
| NOTE_003 | **US_DRIVER_LICENSE** | `9123456789` | 202-212 |
| NOTE_003 | **EMAIL** | `vikram.iyer@medmail.in` | 221-243 |
| NOTE_003 | **MRN** | `MRN-10098` | 250-259 |
| NOTE_003 | **AADHAAR** | `987654321234` | 269-281 |
| NOTE_003 | **US_DRIVER_LICENSE** | `560034` | 320-326 |
| NOTE_003 | **PERSON** | `Nisha Rao` | 344-353 |
| NOTE_004 | **PERSON** | `Emily Turner` | 8-20 |
| NOTE_004 | **DATE** | `March 12 2026` | 34-47 |
| NOTE_004 | **DATE** | `03/19/2026` | 61-71 |
| NOTE_004 | **EMAIL** | `emily.turner@westbrookhealth.com` | 195-227 |
| NOTE_004 | **PHONE** | `646-555-3819` | 236-248 |
| NOTE_004 | **SSN** | `239-40-7711` | 255-266 |
| NOTE_004 | **MRN** | `MRN-55007` | 273-282 |
| NOTE_004 | **LOCATION** | `Newark` | 310-316 |
| NOTE_004 | **ORGANIZATION** | `NJ` | 318-320 |
| NOTE_004 | **ZIP** | `07102` | 321-326 |
| NOTE_004 | **URL** | `www.westbrookhealth.com/patient-portal.` | 341-380 |
| NOTE_005 | **PERSON** | `Abdul Khan` | 8-18 |
| NOTE_005 | **DATE** | `22/08/1978` | 25-35 |
| NOTE_005 | **DATE** | `2026-06-02` | 56-66 |
| NOTE_005 | **DATE** | `2026-06-04` | 82-92 |
| NOTE_005 | **PHONE** | `+91-99887-66554` | 112-127 |
| NOTE_005 | **US_DRIVER_LICENSE** | `9988766554` | 144-154 |
| NOTE_005 | **EMAIL** | `abdul.khan@citycare.in` | 163-185 |
| NOTE_005 | **AADHAAR** | `4567 1234 8890` | 196-210 |
| NOTE_005 | **MRN** | `MRN-32011` | 217-226 |
| NOTE_005 | **US_DRIVER_LICENSE** | `302001` | 263-269 |
| NOTE_005 | **IP** | `10.14.22.9` | 293-303 |
| NOTE_005 | **PERSON** | `Ritu Sengar` | 328-339 |
| NOTE_005 | **PERSON** | `Harsh Vardhan` | 357-370 |
| NOTE_006 | **PERSON** | `Laura Mitchell` | 8-22 |
| NOTE_006 | **PHONE_NUMBER** | `04-09-2026` | 31-41 |
| NOTE_006 | **DATE** | `April 16 2026` | 80-93 |
| NOTE_006 | **PHONE** | `(415) 555-2840` | 101-115 |
| NOTE_006 | **PHONE** | `415-555-0028` | 133-145 |
| NOTE_006 | **EMAIL** | `l.mitchell@bayareahealth.net` | 154-182 |
| NOTE_006 | **SSN** | `533-18-6245` | 188-199 |
| NOTE_006 | **MRN** | `MRN-44590` | 206-215 |
| NOTE_006 | **LOCATION** | `San Francisco` | 239-252 |
| NOTE_006 | **DATE_TIME** | `CA 94107` | 254-262 |
| NOTE_006 | **US_SSN** | `94107-3119` | 289-299 |
| NOTE_006 | **PERSON** | `Alan Reed` | 317-326 |
| NOTE_006 | **PERSON** | `Susan Park` | 334-344 |
| NOTE_007 | **PERSON** | `Neha Desai` | 8-18 |
| NOTE_007 | **DATE** | `11/01/1993` | 24-34 |
| NOTE_007 | **DATE** | `01/07/2026` | 52-62 |
| NOTE_007 | **DATE** | `05/07/2026` | 79-89 |
| NOTE_007 | **PHONE** | `+91 98765 12345` | 190-205 |
| NOTE_007 | **US_DRIVER_LICENSE** | `9876512345` | 210-220 |
| NOTE_007 | **EMAIL** | `neha.desai@apolloexample.com` | 228-256 |
| NOTE_007 | **MRN** | `MRN-77880` | 263-272 |
| NOTE_007 | **AADHAAR** | `2345 6789 1201` | 282-296 |
| NOTE_007 | **US_DRIVER_LICENSE** | `380009` | 342-348 |
| NOTE_007 | **URL** | `www.apolloexample.com/cases.` | 357-385 |
| NOTE_008 | **PERSON** | `Robert Hayes` | 8-20 |
| NOTE_008 | **DATE** | `2026-05-10` | 32-42 |
| NOTE_008 | **PHONE** | `202-555-0144` | 102-114 |
| NOTE_008 | **PHONE** | `(202) 555-2711` | 126-140 |
| NOTE_008 | **EMAIL** | `robert.hayes@metrocare.us` | 148-173 |
| NOTE_008 | **SSN** | `667-24-8931` | 180-191 |
| NOTE_008 | **MRN** | `MRN-91002` | 198-207 |
| NOTE_008 | **LOCATION** | `Washington` | 235-245 |
| NOTE_008 | **DATE_TIME** | `20009` | 250-255 |
| NOTE_008 | **IP** | `172.16.44.101` | 280-293 |
| NOTE_008 | **PERSON** | `Priya Nair` | 319-329 |
| NOTE_008 | **PERSON** | `George Allen` | 355-367 |
| NOTE_009 | **PERSON** | `Kavya Menon` | 8-19 |
| NOTE_009 | **DATE** | `June 5 2026` | 51-62 |
| NOTE_009 | **DATE** | `12-06-2026` | 86-96 |
| NOTE_009 | **US_DRIVER_LICENSE** | `9765432109` | 105-115 |
| NOTE_009 | **PHONE** | `+91-97654-32109` | 134-149 |
| NOTE_009 | **EMAIL** | `kavya.menon@skinwell.in` | 157-180 |
| NOTE_009 | **AADHAAR** | `1122 3344 5566` | 190-204 |
| NOTE_009 | **ORGANIZATION** | `MRN MRN-66543` | 206-219 |
| NOTE_009 | **LOCATION** | `Green Park` | 241-251 |
| NOTE_009 | **DATE_TIME** | `Kochi 682020` | 253-265 |
| NOTE_009 | **PERSON** | `Meera Das` | 279-288 |
| NOTE_010 | **PERSON** | `Jacob Miller` | 8-20 |
| NOTE_010 | **DATE** | `07/21/1982` | 27-37 |
| NOTE_010 | **DATE** | `07-28-2026` | 55-65 |
| NOTE_010 | **DATE** | `2026-08-11` | 70-80 |
| NOTE_010 | **PHONE** | `718-555-6620` | 92-104 |
| NOTE_010 | **EMAIL** | `jacob.miller@eastbridge.org` | 109-136 |
| NOTE_010 | **SSN** | `314-55-9002` | 142-153 |
| NOTE_010 | **MRN** | `MRN-77210` | 160-169 |
| NOTE_010 | **LOCATION** | `Street` | 194-200 |
| NOTE_010 | **LOCATION** | `New York` | 202-210 |
| NOTE_010 | **US_SSN** | `10065-4120` | 215-225 |
| NOTE_010 | **URL** | `https://eastbridge.org/results.` | 239-270 |
| NOTE_010 | **PERSON** | `Helena Cruz` | 287-298 |
| NOTE_010 | **PERSON** | `Omar Patel` | 319-329 |
| NOTE_011 | **PERSON** | `Isha Gupta` | 8-18 |
| NOTE_011 | **DATE** | `09/06/2026` | 49-59 |
| NOTE_011 | **DATE** | `14/06/2026` | 82-92 |
| NOTE_011 | **US_DRIVER_LICENSE** | `9012345678` | 100-110 |
| NOTE_011 | **PHONE** | `+91 90123 45678` | 116-131 |
| NOTE_011 | **EMAIL** | `isha.gupta@caremail.in` | 139-161 |
| NOTE_011 | **AADHAAR** | `7788 9900 1122` | 172-186 |
| NOTE_011 | **MRN** | `MRN-24567` | 193-202 |
| NOTE_011 | **US_DRIVER_LICENSE** | `226001` | 237-243 |
| NOTE_011 | **IP** | `192.168.200.45` | 261-275 |
| NOTE_011 | **PERSON** | `Rohit Sen` | 294-303 |
| NOTE_011 | **PERSON** | `Isha Gupta` | 318-328 |
| NOTE_012 | **PERSON** | `Matthew Clark` | 8-21 |
| NOTE_012 | **DATE** | `February 3 2026` | 48-63 |
| NOTE_012 | **DATE** | `02/10/2026` | 81-91 |
| NOTE_012 | **PHONE** | `(503) 555-1299` | 100-114 |
| NOTE_012 | **PHONE** | `503-555-7781` | 126-138 |
| NOTE_012 | **EMAIL** | `m.clark@rainierclinic.com` | 146-171 |
| NOTE_012 | **SSN** | `808-33-4501` | 178-189 |
| NOTE_012 | **MRN** | `MRN-60991` | 196-205 |
| NOTE_012 | **PERSON** | `Alder St` | 224-232 |
| NOTE_012 | **LOCATION** | `Portland` | 234-242 |
| NOTE_012 | **DATE_TIME** | `97205` | 247-252 |
| NOTE_012 | **URL** | `www.rainierclinic.com/login.` | 270-298 |
| NOTE_012 | **PERSON** | `Elena Moore` | 311-322 |
| NOTE_012 | **PERSON** | `Victor James` | 340-352 |
| NOTE_013 | **PERSON** | `Harpreet Singh` | 8-22 |
| NOTE_013 | **DATE** | `1991-03-18` | 28-38 |
| NOTE_013 | **DATE** | `18-03-2026` | 57-67 |
| NOTE_013 | **PHONE** | `+91-88990-11223` | 107-122 |
| NOTE_013 | **US_DRIVER_LICENSE** | `8899011223` | 134-144 |
| NOTE_013 | **EMAIL** | `harpreet.singh@spinecare.in` | 152-179 |
| NOTE_013 | **ORGANIZATION** | `Aadhaar 6655` | 181-193 |
| NOTE_013 | **DATE_TIME** | `4433 2211` | 194-203 |
| NOTE_013 | **MRN** | `MRN-34220` | 210-219 |
| NOTE_013 | **US_DRIVER_LICENSE** | `160017` | 255-261 |
| NOTE_013 | **URL** | `https://spinecare.in/appointments.` | 271-305 |
| NOTE_013 | **PERSON** | `Kavita Malhotra` | 327-342 |
| NOTE_013 | **PERSON** | `S. Banerjee` | 360-371 |
| NOTE_014 | **PERSON** | `Olivia Reed` | 8-19 |
| NOTE_014 | **DATE** | `2026-09-01` | 28-38 |
| NOTE_014 | **DATE** | `September 8 2026` | 79-95 |
| NOTE_014 | **PHONE** | `404-555-8001` | 124-136 |
| NOTE_014 | **PHONE** | `(404) 555-3322` | 141-155 |
| NOTE_014 | **EMAIL** | `o.reed@atlanticmindhealth.com` | 164-193 |
| NOTE_014 | **SSN** | `921-77-6108` | 199-210 |
| NOTE_014 | **MRN** | `MRN-51444` | 216-225 |
| NOTE_014 | **ORGANIZATION** | `Peachtree Blvd` | 239-253 |
| NOTE_014 | **LOCATION** | `Atlanta` | 255-262 |
| NOTE_014 | **DATE_TIME** | `30309` | 267-272 |
| NOTE_014 | **IP** | `203.0.113.19` | 284-296 |
| NOTE_014 | **PERSON** | `Ian Foster` | 314-324 |
| NOTE_015 | **PERSON** | `Farah Ali` | 8-17 |
| NOTE_015 | **DATE** | `13/07/2026` | 31-41 |
| NOTE_015 | **PHONE_NUMBER** | `07-20-2026` | 78-88 |
| NOTE_015 | **US_DRIVER_LICENSE** | `9345678901` | 100-110 |
| NOTE_015 | **PHONE** | `+91 93456 78901` | 112-127 |
| NOTE_015 | **EMAIL** | `farah.ali@metrohospital.in` | 135-161 |
| NOTE_015 | **AADHAAR** | `9900 7766 5544` | 172-186 |
| NOTE_015 | **MRN** | `MRN-80818` | 193-202 |
| NOTE_015 | **ORGANIZATION** | `101 Palm Residency` | 213-231 |
| NOTE_015 | **DATE_TIME** | `Pune 411001` | 233-244 |
| NOTE_015 | **URL** | `www.metrohospital.in/help.` | 259-285 |
| NOTE_015 | **PERSON** | `Rhea Kapoor` | 301-312 |
| NOTE_015 | **PERSON** | `Farah Ali` | 322-331 |
| NOTE_015 | **PERSON** | `Daniel Ross` | 348-359 |
| NOTE_016 | **PERSON** | `John Smith` | 9-19 |
| NOTE_016 | **DATE** | `14/02/1985` | 35-45 |
| NOTE_016 | **DATE** | `05/06/2026` | 56-66 |
| NOTE_016 | **PHONE** | `(555) 019-2834` | 77-91 |
| NOTE_016 | **SSN** | `666-29-9012` | 97-108 |
| NOTE_016 | **LOCATION** | `MG Road` | 121-128 |
| NOTE_016 | **LOCATION** | `Mumbai` | 130-136 |
| NOTE_016 | **ORGANIZATION** | `Maharashtra 400001` | 138-156 |
| NOTE_016 | **PERSON** | `Emily Carter` | 182-194 |
| NOTE_016 | **DATE_TIME** | `4 days` | 283-289 |
| NOTE_016 | **PERSON** | `Emily Carter` | 377-389 |
| NOTE_017 | **PERSON** | `Rahul Verma
Age` | 14-29 |
| NOTE_017 | **MRN** | `MRN-998822` | 57-67 |
| NOTE_017 | **DATE** | `01/06/2026` | 78-88 |
| NOTE_017 | **EMAIL** | `rahul.verma@outlook.com` | 96-119 |
| NOTE_017 | **PHONE_NUMBER** | `91-98765-43210` | 128-142 |
| NOTE_017 | **ORGANIZATION** | `ECG` | 238-241 |
| NOTE_017 | **PERSON** | `Anil Mehta` | 307-317 |
| NOTE_017 | **ORGANIZATION** | `the Cardiology Wing of` | 321-343 |
| NOTE_018 | **PERSON** | `Sarah Johnson` | 6-19 |
| NOTE_018 | **INSURANCE** | `INS-789012-A` | 42-54 |
| NOTE_018 | **ORGANIZATION** | `Home Address` | 106-118 |
| NOTE_018 | **LOCATION** | `Delhi` | 136-141 |
| NOTE_018 | **US_DRIVER_LICENSE** | `110001` | 142-148 |
| NOTE_018 | **PERSON** | `Mike Johnson` | 168-180 |
| NOTE_018 | **US_DRIVER_LICENSE** | `9123456780` | 199-209 |
| NOTE_018 | **PERSON** | `Priya Nair` | 235-245 |
| NOTE_018 | **LICENSE** | `MH-2024-7890` | 259-271 |
| NOTE_019 | **DATE** | `June 12, 2026` | 6-19 |
| NOTE_019 | **PERSON** | `Robert 'Bob'` | 29-41 |
| NOTE_019 | **PERSON** | `Taylor` | 42-48 |
| NOTE_019 | **PHONE_NUMBER** | `09-18-1972` | 55-65 |
| NOTE_019 | **ORGANIZATION** | `IP Address of Device` | 67-87 |
| NOTE_019 | **IP** | `192.168.1.104` | 89-102 |
| NOTE_019 | **EMAIL** | `rtaylor72@yahoo.com` | 110-129 |
| NOTE_019 | **PERSON** | `Sarah Jenkins` | 280-293 |
| NOTE_020 | **PERSON** | `Alice Green
Age` | 9-24 |
| NOTE_020 | **DATE** | `03/15/2026` | 44-54 |
| NOTE_020 | **URL** | `https://clinical-portal.local/records/g-89211` | 60-105 |
| NOTE_020 | **DATE_TIME** | `4 weeks` | 273-280 |
| NOTE_020 | **PERSON** | `James Andrews` | 290-303 |
