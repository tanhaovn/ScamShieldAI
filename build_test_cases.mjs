import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const OUT_DIR = "D:/scam-detector/outputs/01a1f88b-8092-7493-9320-64f6cf99cc36/test-cases";
const PREVIEW_DIR = path.join(OUT_DIR, "previews");
const FONT = "Arial";
const NAVY = "#17365D";
const BLUE = "#D9EAF7";
const PALE = "#F4F8FB";
const BORDER = "#D9D9D9";
const INPUT = "#FFF2CC";

const c = (id, scenario, type, priority, pre, steps, data, expected) => ({id, scenario, type, priority, pre, steps, data, expected});

const sprints = [
  {
    no: 1, period: "Week 1 to Week 3", owner: "Dao Thi My Nhung",
    modules: [
      {sheet:"Architecture", pb:"PB-01", name:"Project Architecture and Core Scaffolding", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S1_ARCH_001","Start FastAPI application with configured routes","Smoke",5,"Python 3.12 environment and dependencies installed","1. Start Uvicorn.\n2. Call the health endpoint.\n3. Inspect route and startup logs.","Configured local backend","Application starts without error, health endpoint returns 200, and structured routing is available."),
        c("TC_SFDS_S1_ARCH_002","Build React application","Build",5,"Node dependencies installed","1. Run the production build.\n2. Review compiler output.\n3. Open the generated application.","React 18 Vite project","Build completes with no blocking error and the application loads correctly."),
        c("TC_SFDS_S1_ARCH_003","Create and query the initial database schema","Integration",5,"Database configuration and migrations available","1. Create a clean database.\n2. Apply schema.\n3. Insert and read a sample record.","Temporary SQLite database","Schema is created successfully and the sample record can be written and read through SQLAlchemy."),
        c("TC_SFDS_S1_ARCH_004","Run automated lint and pytest pipeline","CI",4,"CI workflow configured","1. Push or run the pipeline locally.\n2. Review lint stage.\n3. Review test stage.","Current main branch","Lint and pytest stages execute automatically and publish a clear pass or fail result."),
      ]},
      {sheet:"Authentication", pb:"PB-02", name:"User and Admin Authentication", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S1_AUTH_001","Admin login with valid credentials","Functional",5,"Active admin account exists","1. Submit valid username and password.\n2. Inspect response.\n3. Open an admin endpoint.","Valid admin credentials","Login returns a signed JWT and the token grants access to the permitted admin endpoint."),
        c("TC_SFDS_S1_AUTH_002","Reject invalid credentials","Negative",5,"Login endpoint available","1. Submit a valid username and wrong password.\n2. Inspect response and logs.","Wrong password","API returns HTTP 401 with an informative error and does not issue a token."),
        c("TC_SFDS_S1_AUTH_003","Reject expired or tampered token","Security",5,"A valid token can be generated","1. Use an expired token.\n2. Use a token with a modified signature.\n3. Call an admin endpoint.","Expired and tampered JWT values","Both tokens are rejected and no protected data is returned."),
        c("TC_SFDS_S1_AUTH_004","Allow public scan but block public admin access","Authorization",5,"Public scan and admin routes deployed","1. Submit a public scan without login.\n2. Call an admin route without a token.","Anonymous request","Public scan is accepted while the admin route returns an authorization error."),
      ]},
      {sheet:"URL Detection", pb:"PB-03", name:"PhishVN Lexical URL Detection", created:"Nguyen Phan Duc Tuan", cases:[
        c("TC_SFDS_S1_URL_001","Classify a known benign Vietnamese domain","Model",5,"PhishVN model loaded","1. Submit the URL.\n2. Capture extracted features and score.","https://www.vietcombank.com.vn","Feature extraction completes and the model returns a calibrated low-risk score."),
        c("TC_SFDS_S1_URL_002","Extract IP, punycode and sensitive-token features","Feature",5,"Feature extractor available","1. Submit each URL.\n2. Compare feature flags with the input.","IP URL, xn-- punycode URL, URL containing login and verify","IP usage, punycode, length, entropy, hyphens, and sensitive tokens are detected correctly."),
        c("TC_SFDS_S1_URL_003","Detect a deceptive banking subdomain","Model",5,"Model and extractor available","1. Submit the deceptive URL.\n2. Review risk score and feature evidence.","https://vietcombank.verify-account.example.com","The deceptive subdomain produces elevated risk with relevant lexical evidence."),
        c("TC_SFDS_S1_URL_004","Meet URL inference latency target","Performance",5,"Timing instrumentation enabled","1. Run 100 representative URL scans.\n2. Record processing time.\n3. Calculate p95.","Balanced URL sample","Each query completes within the acceptance target and p95 is below 250 ms."),
      ]},
      {sheet:"Domain Gating", pb:"PB-04", name:"Domain Gating and Trusted Registry", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S1_GATE_001","Force safe result for an official trusted domain","Functional",5,"Whitelist contains official entries","1. Submit an exact official bank domain.\n2. Review gate decision.","Official Vietcombank or gov.vn domain","Whitelist match is recognized and safe gating is applied without a false scam flag."),
        c("TC_SFDS_S1_GATE_002","Immediately block a known malicious domain","Functional",5,"Blacklist contains a test domain","1. Submit the blacklisted domain.\n2. Review response time and score.","Known blacklisted domain","System returns immediate dangerous handling with risk level 100."),
        c("TC_SFDS_S1_GATE_003","Normalize case, scheme, port and trailing dot","Boundary",4,"Registry lookup available","1. Submit equivalent domain forms.\n2. Compare decisions.","HTTPS, uppercase host, default port, trailing dot","All equivalent forms resolve to the same normalized domain and registry decision."),
        c("TC_SFDS_S1_GATE_004","Meet registry lookup overhead target","Performance",5,"Timing instrumentation enabled","1. Execute repeated whitelist and blacklist lookups.\n2. Calculate p95 overhead.","1,000 mixed registry lookups","Lookup overhead remains below 10 ms at p95."),
      ]},
      {sheet:"Brand Classifier", pb:"PB-05", name:"ResNet-18 Brand Impersonation Classifier", created:"Nguyen Phan Duc Tuan", cases:[
        c("TC_SFDS_S1_BRAND_001","Identify a supported bank logo in a phishing screenshot","Model",5,"ResNet-18 artifact loaded","1. Upload labeled screenshot.\n2. Review brand and fraud scores.","Counterfeit banking login screenshot","Expected brand is identified and visual fraud confidence is elevated."),
        c("TC_SFDS_S1_BRAND_002","Avoid false brand match on a neutral image","Negative",5,"Model loaded","1. Upload neutral screenshot.\n2. Review prediction and confidence.","Plain settings or landscape image","No unsupported high-confidence brand impersonation result is produced."),
        c("TC_SFDS_S1_BRAND_003","Apply temperature scaling to logits","Calibration",5,"Raw and calibrated outputs accessible","1. Run a fixed image.\n2. Capture logits.\n3. Apply T=1.8.\n4. Compare probabilities.","Fixed labeled image","Calibrated probabilities are within 0 to 1, sum correctly, and are less overconfident than raw softmax."),
        c("TC_SFDS_S1_BRAND_004","Handle corrupt or unsupported image safely","Negative",4,"Upload endpoint available","1. Upload corrupt bytes with an image extension.\n2. Inspect response and logs.","Corrupt JPEG payload","System rejects the file with a clear validation error and does not crash the model process."),
      ]},
    ]
  },
  {
    no: 2, period: "Week 4 to Week 6", owner: "Dao Thi My Nhung",
    modules: [
      {sheet:"Image Forensics", pb:"PB-06", name:"Forensics and Compression Artifact Analysis", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S2_ELA_001","Detect edited text in a recompressed receipt","Forensic",4,"ELA pipeline available","1. Upload manipulated JPEG.\n2. Run ELA.\n3. Review anomaly map.","Receipt with edited amount","High-frequency anomaly is highlighted around the edited text area."),
        c("TC_SFDS_S2_ELA_002","Avoid strong anomaly on an unedited image","Negative",4,"ELA pipeline available","1. Upload original JPEG.\n2. Run ELA.\n3. Compare anomaly intensity.","Unedited camera image","ELA result does not show a concentrated false manipulation region."),
        c("TC_SFDS_S2_ELA_003","Extract available EXIF metadata","Functional",4,"Metadata extractor available","1. Upload image with known EXIF.\n2. Compare returned fields.","JPEG with timestamp, camera and software tags","Creation time and available camera or software signatures match the source metadata."),
        c("TC_SFDS_S2_ELA_004","Handle missing EXIF and PNG input","Boundary",3,"Pipeline accepts PNG","1. Upload PNG without EXIF.\n2. Review response.","PNG screenshot","Image is processed without failure and missing metadata is reported as unavailable, not fabricated."),
      ]},
      {sheet:"Vietnamese OCR", pb:"PB-07", name:"Tesseract Vietnamese OCR Engine", created:"Nguyen Phan Duc Tuan", cases:[
        c("TC_SFDS_S2_OCR_001","Extract clear Vietnamese scam text","OCR",5,"vie and eng language packs installed","1. Upload clear screenshot.\n2. Run preprocessing and OCR.\n3. Compare text.","Screenshot containing Vietnamese diacritics","Extracted text preserves the main words and Vietnamese diacritics with usable confidence."),
        c("TC_SFDS_S2_OCR_002","Extract mixed Vietnamese and English text","OCR",4,"OCR engine configured for vie+eng","1. Upload mixed-language screenshot.\n2. Compare result.","Vietnamese message with English URL and brand","Both language segments are extracted in one result without dropping the URL or brand."),
        c("TC_SFDS_S2_OCR_003","Improve noisy image through preprocessing","Integration",5,"Preprocessing stages enabled","1. OCR the raw noisy image.\n2. Apply grayscale, threshold and denoise.\n3. OCR again.","Low-contrast noisy screenshot","Preprocessed result is at least as complete and has higher or equal confidence than the raw result."),
        c("TC_SFDS_S2_OCR_004","Handle blank or unreadable image","Negative",4,"OCR endpoint available","1. Upload blank and severely blurred images.\n2. Review result.","Blank PNG and blurred JPEG","System returns empty or low-confidence text with a clear indication and no server error."),
      ]},
      {sheet:"Risk Keywords", pb:"PB-08", name:"Vietnamese Contextual Risk Keyword Engine", created:"Dao Thi My Nhung", cases:[
        c("TC_SFDS_S2_KEY_001","Detect impersonation and financial urgency","Functional",5,"Keyword lexicon loaded","1. Submit scam message.\n2. Review matched categories and score.","Tôi là công an, chuyển khoản phạt ngay","Impersonation and urgency terms are highlighted and the normalized risk score increases."),
        c("TC_SFDS_S2_KEY_002","Extract OTP request, phone and bank account","Regex",5,"Regex rules loaded","1. Submit structured scam message.\n2. Review extracted entities.","Gửi OTP 123456 tới 090... và chuyển vào 0123456789","OTP solicitation, phone number, and bank account pattern are detected without exposing secrets in logs."),
        c("TC_SFDS_S2_KEY_003","Avoid false positive on benign security advice","Negative",5,"Lexicon loaded","1. Submit benign educational message.\n2. Review matches and score.","Không bao giờ cung cấp OTP cho người khác","Negation and benign context do not produce an unjustified dangerous verdict."),
        c("TC_SFDS_S2_KEY_004","Normalize keyword score","Boundary",4,"Scoring engine available","1. Submit messages with zero, one and many matches.\n2. Compare scores.","Controlled message set","Score remains within 0 to 1 and increases consistently with supported risk evidence."),
      ]},
      {sheet:"Reasoning Engine", pb:"PB-09", name:"Multimodal Consensus Reasoning", created:"Nguyen Phan Duc Tuan", cases:[
        c("TC_SFDS_S2_REASON_001","Return safe consensus when all evidence is safe","Integration",5,"All evidence engines available","1. Submit trusted URL, benign text and neutral image.\n2. Review four reasoning steps.","Safe multimodal bundle","Domain, visual, text and consensus steps support a low-risk verdict."),
        c("TC_SFDS_S2_REASON_002","Raise risk when strong text evidence conflicts with neutral image","Integration",5,"Fusion engine available","1. Submit neutral image and high-risk text.\n2. Review weights and final score.","Neutral image plus OTP scam text","Final result reflects strong linguistic evidence and explains the conflicting signals."),
        c("TC_SFDS_S2_REASON_003","Avoid extreme jump for ambiguous evidence","Calibration",5,"Soft voting enabled","1. Submit borderline evidence combinations.\n2. Repeat scans.\n3. Compare scores.","Ambiguous URL, weak logo, mild urgency","Scores remain stable and do not jump without justification between near-zero and near-one extremes."),
        c("TC_SFDS_S2_REASON_004","Expose complete reasoning sequence","Functional",4,"Reasoning response schema available","1. Submit multimodal evidence.\n2. Inspect API response.","URL, text and image bundle","Response includes Domain, Visual, Text and Consensus steps with confidence-weighted final score."),
      ]},
      {sheet:"Explanation", pb:"PB-10", name:"Human-Readable Explanation Generator", created:"Tran Hoang Nhat Nam", cases:[
        c("TC_SFDS_S2_EXPL_001","Explain a deceptive domain","Functional",4,"URL evidence available","1. Scan deceptive domain.\n2. Review Vietnamese explanation.","Deceptive banking subdomain","Explanation states that the domain imitates a trusted organization and identifies the relevant evidence."),
        c("TC_SFDS_S2_EXPL_002","Explain urgency and OTP evidence","Functional",4,"Keyword evidence available","1. Scan scam message.\n2. Review explanation bullets.","Urgent OTP request","Explanation mentions urgency and OTP solicitation and provides a specific safety action."),
        c("TC_SFDS_S2_EXPL_003","Explain a safe result without alarmist language","Negative",4,"Safe result available","1. Scan trusted benign input.\n2. Review wording.","Official trusted domain","Explanation is calm, clear, and does not invent risk evidence."),
        c("TC_SFDS_S2_EXPL_004","Keep entities synchronized with evidence","Consistency",5,"Entity extraction available","1. Scan input containing a brand and phone.\n2. Compare explanation with evidence object.","Impersonation message","Brand, domain, keyword and entity names in the explanation match the detected evidence exactly."),
      ]},
    ]
  },
  {
    no: 3, period: "Week 7 to Week 9", owner: "Dao Thi My Nhung",
    modules: [
      {sheet:"Scan Interface", pb:"PB-11", name:"Multimodal Scan Submission Interface", created:"Tran Hoang Nhat Nam", cases:[
        c("TC_SFDS_S3_SCAN_001","Submit a URL from the public scan page","UI",5,"Frontend and API running","1. Open URL tab.\n2. Enter URL.\n3. Submit.\n4. Observe result.","Valid suspicious URL","Input is validated, request is sent, progress is shown, and the result page opens."),
        c("TC_SFDS_S3_SCAN_002","Submit free text","UI",5,"Text scan available","1. Open Text tab.\n2. Enter message.\n3. Submit.","Vietnamese scam message","Text is submitted without truncation and the returned evidence is displayed."),
        c("TC_SFDS_S3_SCAN_003","Validate image type and 10 MB limit","Boundary",5,"Image uploader available","1. Upload valid JPEG, PNG and WebP.\n2. Upload unsupported type.\n3. Upload file above 10 MB.","Supported and invalid files","Supported files are accepted; invalid type and oversize file are rejected before processing with clear messages."),
        c("TC_SFDS_S3_SCAN_004","Show responsive progress and prevent duplicate submission","Usability",4,"Slow test response can be simulated","1. Submit on desktop and mobile width.\n2. Click submit repeatedly.\n3. Observe loading state.","Delayed API response","Layout remains usable, progress is visible, and duplicate requests are prevented."),
      ]},
      {sheet:"Risk Visualization", pb:"PB-12", name:"Visual Explanation and Risk Gauge", created:"Tran Hoang Nhat Nam", cases:[
        c("TC_SFDS_S3_VIS_001","Apply risk gauge boundaries","Boundary",4,"Result screen available","1. Display scores 0, 39, 40, 69, 70 and 100.\n2. Check label and color.","Boundary score fixtures","0-39 is Safe, 40-69 is Suspicious, and 70-100 is Dangerous with correct colors."),
        c("TC_SFDS_S3_VIS_002","Match radar chart to evidence scores","Consistency",4,"Evidence scores returned","1. Open result.\n2. Compare chart values with API data.","Known domain, visual, linguistic and urgency scores","All radar axes match the response values and remain within the chart scale."),
        c("TC_SFDS_S3_VIS_003","Show actionable advice for dangerous result","Usability",5,"Dangerous fixture available","1. Open dangerous result.\n2. Review recommendations.","OTP and fake-bank scam result","Page advises the user not to provide OTP and to contact the bank through an official channel."),
        c("TC_SFDS_S3_VIS_004","Render safe result without dangerous styling","Negative",4,"Safe fixture available","1. Open safe result.\n2. Inspect gauge, chart and advice.","Trusted-domain safe result","Safe styling and advice are consistent and no dangerous warning is shown."),
      ]},
      {sheet:"History", pb:"PB-13", name:"Local Inspection History and Offline Cache", created:"Tran Hoang Nhat Nam", cases:[
        c("TC_SFDS_S3_HIST_001","Persist recent scan after browser reload","Functional",3,"History enabled","1. Complete a scan.\n2. Reload browser.\n3. Open History.","One completed scan","The scan remains available with timestamp, risk label and summary."),
        c("TC_SFDS_S3_HIST_002","Keep only the 50 most recent records","Boundary",3,"History storage clear","1. Create 51 scan records.\n2. Open History.\n3. Count and inspect oldest record.","51 generated records","History contains 50 records and removes only the oldest record."),
        c("TC_SFDS_S3_HIST_003","Confirm before clearing history","UI",3,"History contains records","1. Click Clear.\n2. Cancel.\n3. Click Clear and confirm.","Existing history","Cancel preserves all records; confirmation removes them and updates the empty state."),
        c("TC_SFDS_S3_HIST_004","Replay full details from history","Functional",3,"Saved record contains reasoning","1. Search for record.\n2. Open detail modal.\n3. Compare with original.","Saved multimodal result","Modal restores the original score, evidence, explanations and advice without rerunning the scan."),
      ]},
      {sheet:"Feedback", pb:"PB-14", name:"Incident Feedback and False Result Reporting", created:"Dao Thi My Nhung", cases:[
        c("TC_SFDS_S3_FEED_001","Report a false positive","Functional",3,"Completed scan result visible","1. Open Report Incorrect Result.\n2. Select false positive.\n3. Enter explanation.\n4. Submit.","Valid explanation","Feedback is accepted, linked to the scan, and saved with Pending status."),
        c("TC_SFDS_S3_FEED_002","Submit without optional email","Boundary",3,"Feedback modal open","1. Fill required fields.\n2. Leave email blank.\n3. Submit.","No email","Submission succeeds because contact email is optional."),
        c("TC_SFDS_S3_FEED_003","Reject invalid email and empty explanation","Negative",3,"Feedback modal open","1. Enter invalid email and empty explanation.\n2. Submit.","Invalid email","Inline validation identifies the invalid fields and no feedback record is created."),
        c("TC_SFDS_S3_FEED_004","Show confirmation after successful submission","Usability",3,"API available","1. Submit valid feedback.\n2. Observe UI.\n3. Query saved record.","Valid feedback","Confirmation toast is shown once and database record contains type, explanation, optional contact and Pending status."),
      ]},
    ]
  },
  {
    no: 4, period: "Week 10 to Week 12", owner: "Dao Thi My Nhung",
    modules: [
      {sheet:"Incident Triage", pb:"PB-15", name:"Admin Incident Triage and Verification Queue", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S4_TRIAGE_001","List incidents with pagination and status filter","Functional",4,"Admin logged in and incidents exist","1. Open queue.\n2. Change page.\n3. Filter Pending, Reviewed and Dismissed.","Mixed incident records","Rows, totals and pagination update correctly for each status."),
        c("TC_SFDS_S4_TRIAGE_002","Open full incident detail","Functional",4,"Incident exists","1. Open an incident.\n2. Compare fields with database.","Incident with URL, image, scores and remarks","Detail shows original inputs, AI scores, evidence and user remarks accurately."),
        c("TC_SFDS_S4_TRIAGE_003","Verify or dismiss an incident","State",4,"Pending incident exists","1. Click Verify on one record.\n2. Click Dismiss on another.\n3. Reload queue.","Two pending incidents","Statuses persist, action metadata is recorded, and records move to the correct filters."),
        c("TC_SFDS_S4_TRIAGE_004","Block non-admin access","Security",5,"Public user and admin route available","1. Call queue endpoint without token.\n2. Call with non-admin token.","Unauthorized requests","Both requests are rejected and no incident evidence is disclosed."),
      ]},
      {sheet:"Metrics Dashboard", pb:"PB-16", name:"Threat Intelligence and Real-time Metrics", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S4_METRIC_001","Calculate headline KPIs accurately","Data",4,"Known scan dataset loaded","1. Open dashboard.\n2. Independently calculate totals and rates.\n3. Compare.","Controlled scans and feedback dataset","Total scans, confirmed scam percentage, average response time and false-positive rate match the source data."),
        c("TC_SFDS_S4_METRIC_002","Display daily scan and risk trends","UI",4,"Multi-day data available","1. Select date range.\n2. Compare chart points with grouped records.","Seven-day scan dataset","Daily volume and risk distribution charts use the correct dates and counts."),
        c("TC_SFDS_S4_METRIC_003","Rank targeted brands","Data",4,"Brand labels available","1. Open leaderboard.\n2. Independently count brands.\n3. Compare order.","Known brand-frequency dataset","Brands are ranked by count with correct values and deterministic tie handling."),
        c("TC_SFDS_S4_METRIC_004","Handle empty period","Boundary",3,"Date filter available","1. Select a range with no scans.\n2. Observe all widgets.","Empty date range","Dashboard shows zero or no-data states without broken charts, NaN values or server errors."),
      ]},
      {sheet:"Protection Lists", pb:"PB-17", name:"Dynamic Whitelist and Blacklist Manager", created:"Nguyen Phan Duc Tuan", cases:[
        c("TC_SFDS_S4_LIST_001","Create, update and delete whitelist rule","CRUD",4,"Admin logged in","1. Add trusted domain.\n2. Update note.\n3. Run lookup.\n4. Delete rule.","trusted-example.vn","Rule changes persist and lookup behavior reflects each change."),
        c("TC_SFDS_S4_LIST_002","Add blacklist rule and invalidate cache","Integration",5,"Inference cache enabled","1. Scan domain before rule.\n2. Add blacklist rule.\n3. Scan again immediately.","new-phish-example.test","Second scan uses the new rule immediately and returns dangerous handling."),
        c("TC_SFDS_S4_LIST_003","Reject invalid or unsafe regex rule","Negative",4,"Regex editor available","1. Submit malformed regex.\n2. Submit expensive unsafe pattern.\n3. Save.","Malformed and catastrophic patterns","Validation rejects invalid rules and leaves the active configuration unchanged."),
        c("TC_SFDS_S4_LIST_004","Manage weighted risk keyword","Functional",4,"Keyword manager available","1. Add keyword and weight.\n2. Scan matching text.\n3. Update weight and rescan.","Test keyword with two weights","Keyword is matched and the normalized score changes consistently with the configured weight."),
      ]},
      {sheet:"Report Export", pb:"PB-18", name:"Detailed Incident Audit Report Export", created:"Dao Thi My Nhung", cases:[
        c("TC_SFDS_S4_EXPORT_001","Export complete PDF incident report","Export",3,"Verified incident exists","1. Open incident.\n2. Export PDF.\n3. Inspect document.","Incident with all evidence types","PDF contains timestamp, scores, forensic highlights, advice, and C1SE.06 verification header."),
        c("TC_SFDS_S4_EXPORT_002","Export CSV with Vietnamese text","Export",3,"Incident log contains Vietnamese data","1. Export CSV.\n2. Open in Excel.\n3. Verify columns and encoding.","Vietnamese incident records","CSV has stable headers, correct rows, UTF-8 Vietnamese text, and no shifted columns."),
        c("TC_SFDS_S4_EXPORT_003","Apply selected filters to export","Functional",3,"Mixed status and date data exists","1. Filter by date and status.\n2. Export.\n3. Compare rows.","Filtered incident set","Export contains only records matching the visible filters."),
        c("TC_SFDS_S4_EXPORT_004","Handle export with no matching data","Boundary",3,"Filter can return zero rows","1. Select empty filter.\n2. Attempt export.","No matching records","System shows a clear no-data message or valid empty export and does not create a corrupt file."),
      ]},
    ]
  },
  {
    no: 5, period: "Week 13 to Week 15", owner: "Dao Thi My Nhung",
    modules: [
      {sheet:"Security Hardening", pb:"PB-19", name:"Rate Limiting and OWASP Security Hardening", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S5_SEC_001","Enforce 30 requests per minute per IP","Security",5,"Rate limiter enabled","1. Send 30 requests in one minute.\n2. Send request 31.\n3. Wait for reset and retry.","Single test IP","Allowed requests succeed, excess request is limited with a clear response, and access resumes after reset."),
        c("TC_SFDS_S5_SEC_002","Reject mismatched MIME type and magic bytes","Security",5,"Upload validation enabled","1. Rename executable bytes as JPEG.\n2. Upload file.\n3. Review storage and logs.","Spoofed image upload","Upload is rejected before model processing and unsafe content is not stored as a valid image."),
        c("TC_SFDS_S5_SEC_003","Restrict CORS origins","Security",5,"CORS allowlist configured","1. Send preflight from allowed origin.\n2. Send from unapproved origin.","Allowed and disallowed origins","Allowed origin receives correct CORS headers; disallowed origin is rejected without permissive wildcard headers."),
        c("TC_SFDS_S5_SEC_004","Resist SQL injection and stored XSS payloads","Security",5,"Security test environment isolated","1. Submit SQL injection strings.\n2. Submit script payload in feedback.\n3. Review response and rendered admin view.","Controlled OWASP payloads","Queries remain parameterized, scripts are escaped or sanitized, and no payload executes."),
      ]},
      {sheet:"E2E Regression", pb:"PB-20", name:"End-to-End Regression", created:"Dao Thi My Nhung", cases:[
        c("TC_SFDS_S5_E2E_001","Complete public multimodal scan workflow","System",5,"Integrated build deployed","1. Submit URL, text and image.\n2. Review result.\n3. Save history.\n4. Submit feedback.","Representative scam bundle","Workflow completes with consistent score, evidence, explanation, history and feedback record."),
        c("TC_SFDS_S5_E2E_002","Complete admin review and protection update","System",5,"Pending feedback exists and admin logged in","1. Review incident.\n2. Verify scam.\n3. Add domain to blacklist.\n4. Rescan publicly.","Pending malicious incident","Incident status updates and subsequent public scan uses the new blacklist rule."),
        c("TC_SFDS_S5_E2E_003","Run full automated regression suite","Regression",5,"Unit and integration suites configured","1. Run complete pytest and frontend suites.\n2. Review failures.\n3. Capture coverage.","Release candidate build","All release-blocking tests pass and measured coverage exceeds 85 percent."),
        c("TC_SFDS_S5_E2E_004","Verify all backlog acceptance criteria","Acceptance",5,"PB-01 through PB-20 evidence available","1. Review traceability.\n2. Execute missing priority tests.\n3. Record approval.","Release acceptance checklist","Every backlog item has test evidence and no Critical or High defect remains open."),
      ]},
      {sheet:"Load Test", pb:"PB-20", name:"Load and Stress Testing", created:"Pham Tan Hao", cases:[
        c("TC_SFDS_S5_LOAD_001","Run 50-user steady load","Performance",5,"Production-like environment and Locust script ready","1. Ramp to 50 users.\n2. Hold load.\n3. Capture latency, throughput and errors.","Balanced scan workload","p95 latency remains below 3.0 seconds with acceptable error rate and stable resources."),
        c("TC_SFDS_S5_LOAD_002","Recover after short stress spike","Stress",5,"Monitoring enabled","1. Ramp above normal load briefly.\n2. Return to 50 users.\n3. Observe recovery.","Controlled stress profile","Service does not corrupt data and latency returns toward baseline after the spike."),
        c("TC_SFDS_S5_LOAD_003","Measure mixed URL, text and image workload","Performance",5,"All scan modalities available","1. Run weighted mixed scenario.\n2. Compare modality metrics.","50 percent URL, 30 percent text, 20 percent image","Each modality completes and the overall p95 target is measured without hiding image failures."),
        c("TC_SFDS_S5_LOAD_004","Maintain rate-limit behavior under concurrency","Security Performance",5,"Rate limiter and load test configured","1. Run requests from controlled IP groups.\n2. Inspect limited responses.","Concurrent users with repeated IPs","Rate limit applies per configured IP rule and does not cause unrestricted traffic or server failure."),
      ]},
      {sheet:"Calibration", pb:"PB-20", name:"Model Calibration Validation", created:"Nguyen Phan Duc Tuan", cases:[
        c("TC_SFDS_S5_CAL_001","Check score stability on ambiguous inputs","Calibration",5,"Ambiguous golden set versioned","1. Run each sample repeatedly.\n2. Compare scores and labels.","Ambiguous multimodal set","Scores remain stable and do not alternate between unjustified extreme values."),
        c("TC_SFDS_S5_CAL_002","Check threshold labels around 39, 40, 69 and 70","Boundary",5,"Controlled score fixtures available","1. Produce boundary scores.\n2. Review API and UI labels.","39, 40, 69 and 70 percent fixtures","Labels change exactly at the defined boundaries and match across backend and frontend."),
        c("TC_SFDS_S5_CAL_003","Compare confidence with labeled validation set","Model",5,"Labeled validation set available","1. Run validation set.\n2. Group confidence and correctness.\n3. Review outliers.","Versioned balanced validation set","Calibration evidence is recorded and severe overconfidence cases are identified for review."),
        c("TC_SFDS_S5_CAL_004","Preserve result after repeated identical scan","Consistency",4,"Deterministic preprocessing configured","1. Submit identical input five times.\n2. Compare evidence and scores.","Fixed URL, text and image","Results remain equivalent within the approved numerical tolerance."),
      ]},
    ]
  },
];

function sanitizeSheetRef(name) { return `'${name.replaceAll("'", "''")}'`; }

function styleBase(sheet, usedAddress) {
  sheet.showGridLines = false;
  const used = sheet.getRange(usedAddress);
  used.format.font = { name: FONT, size: 10, color: "#111827" };
  used.format.verticalAlignment = "center";
}

function formatModuleSheet(sheet, sprint, module) {
  const start = 15;
  const end = start + module.cases.length - 1;
  sheet.mergeCells("A1:O1");
  sheet.getRange("A1").values = [[`${module.name} Test Cases`]];
  sheet.getRange("A1:O1").format = {font:{name:FONT,size:15,bold:true,color:"#000000"}, rowHeight:28, verticalAlignment:"center"};
  sheet.getRange("A2:B6").values = [
    ["Project name","Scam Fraud Detection System with Explanations"],
    ["Module name",module.name],
    ["Backlog reference",module.pb],
    ["Created by",module.created],
    ["Sprint",`Sprint ${sprint.no}  ${sprint.period}`],
  ];
  sheet.getRange("A2:A6").format = {font:{name:FONT,bold:true}, fill:BLUE};
  sheet.getRange("A2:B6").format.borders = {preset:"all",style:"thin",color:BORDER};
  sheet.getRange("D2:E6").values = [
    ["Source","C1SE.06 Product Backlog SFDS v1.0"],
    ["Execution state","Planning baseline"],
    ["Status options","Not Run, Pass, Fail, Blocked, N/A"],
    ["Priority scale","5 highest; 1 lowest"],
    ["Version","1.0"],
  ];
  sheet.getRange("D2:D6").format = {font:{name:FONT,bold:true}, fill:BLUE};
  sheet.getRange("D2:E6").format.borders = {preset:"all",style:"thin",color:BORDER};

  sheet.getRange("A8:B13").values = [["Planned",null],["Pass",null],["Fail",null],["Blocked",null],["Not Run",null],["Pass rate",null]];
  sheet.getRange("A8:A13").format = {font:{name:FONT,bold:true}, fill:BLUE};
  sheet.getRange("A8:B13").format.borders = {preset:"all",style:"thin",color:BORDER};
  sheet.getRange("B8").formulas = [[`=COUNTA(A${start}:A${end})`]];
  sheet.getRange("B9").formulas = [[`=COUNTIFS(K${start}:K${end},"Pass")`]];
  sheet.getRange("B10").formulas = [[`=COUNTIFS(K${start}:K${end},"Fail")`]];
  sheet.getRange("B11").formulas = [[`=COUNTIFS(K${start}:K${end},"Blocked")`]];
  sheet.getRange("B12").formulas = [[`=COUNTIFS(K${start}:K${end},"Not Run")`]];
  sheet.getRange("B13").formulas = [[`=IF(B8=0,0,B9/B8)`]];
  sheet.getRange("B13").format.numberFormat = "0.0%";

  const headers = ["Test Case ID","PB Ref","Scenario","Type","Priority","Preconditions","Test Steps","Test Data","Expected Result","Actual Result","Status","Executor","Build","Defect Ref","Execution Date"];
  sheet.getRange("A14:O14").values = [headers];
  sheet.getRange("A14:O14").format = {fill:NAVY,font:{name:FONT,size:10,bold:true,color:"#FFFFFF"},horizontalAlignment:"center",verticalAlignment:"center",wrapText:true,rowHeight:34,borders:{preset:"all",style:"thin",color:"#FFFFFF"}};
  const rows = module.cases.map(x => [x.id,module.pb,x.scenario,x.type,x.priority,x.pre,x.steps,x.data,x.expected,"","Not Run","","","",null]);
  sheet.getRange(`A${start}:O${end}`).values = rows;
  sheet.getRange(`A${start}:O${end}`).format = {wrapText:true,verticalAlignment:"top",borders:{preset:"all",style:"thin",color:BORDER}};
  for (let r = start; r <= end; r++) {
    if ((r-start)%2 === 1) sheet.getRange(`A${r}:I${r}`).format.fill = PALE;
    sheet.getRange(`A${r}:O${r}`).format.rowHeight = 72;
  }
  sheet.getRange(`J${start}:O${end}`).format.fill = INPUT;
  sheet.getRange(`E${start}:E${end}`).format.horizontalAlignment = "center";
  sheet.getRange(`K${start}:O${end}`).format.horizontalAlignment = "center";
  sheet.getRange(`O${start}:O${end}`).format.numberFormat = "dd/mm/yyyy";
  sheet.getRange(`K${start}:K${end}`).dataValidation = {rule:{type:"list",values:["Not Run","Pass","Fail","Blocked","N/A"]}};
  sheet.getRange(`E${start}:E${end}`).dataValidation = {rule:{type:"list",values:["1","2","3","4","5"]}};
  const statusRange = sheet.getRange(`K${start}:K${end}`);
  statusRange.conditionalFormats.add("containsText",{text:"Pass",format:{fill:"#E2F0D9",font:{bold:true,color:"#385723"}}});
  statusRange.conditionalFormats.add("containsText",{text:"Fail",format:{fill:"#FCE4D6",font:{bold:true,color:"#C00000"}}});
  statusRange.conditionalFormats.add("containsText",{text:"Blocked",format:{fill:"#F4B183",font:{bold:true,color:"#7F6000"}}});
  statusRange.conditionalFormats.add("containsText",{text:"Not Run",format:{fill:"#FFF2CC",font:{color:"#7F6000"}}});

  const widths = [23,10,28,14,9,30,42,26,40,34,12,18,16,16,16];
  widths.forEach((w,i)=>sheet.getRangeByIndexes(0,i,end,1).format.columnWidth=w);
  sheet.freezePanes.freezeRows(14);
  sheet.freezePanes.freezeColumns(2);
  sheet.tabColor = "#5B9BD5";
  styleBase(sheet,`A1:O${end}`);
  return {end};
}

function buildReport(sheet, sprint) {
  const n = sprint.modules.length;
  const start = 8;
  const end = start+n-1;
  const total = end+1;
  const indicatorHeader = total+2;
  const indicatorStart = indicatorHeader+1;
  const indicatorEnd = indicatorHeader+4;
  sheet.mergeCells("A1:H1");
  sheet.getRange("A1").values = [[`Sprint ${sprint.no} Test Report`]];
  sheet.getRange("A1:H1").format = {font:{name:FONT,size:15,bold:true,color:"#000000"},rowHeight:28};
  sheet.getRange("A3:B6").values = [["Project name","Scam Fraud Detection System with Explanations"],["Prepared by","Team C1SE.06"],["Reviewer","Dao Thi My Nhung  QA Lead"],["Sprint period",sprint.period]];
  sheet.getRange("A3:A6").format = {fill:BLUE,font:{name:FONT,bold:true}};
  sheet.getRange("A3:B6").format.borders = {preset:"all",style:"thin",color:BORDER};
  sheet.getRange("D3:E6").values = [["Version","1.0"],["Source","C1SE.06 Product Backlog SFDS v1.0"],["Execution state","Planning baseline"],["Update rule","Enter actual results in module sheets"]];
  sheet.getRange("D3:D6").format = {fill:BLUE,font:{name:FONT,bold:true}};
  sheet.getRange("D3:E6").format.borders = {preset:"all",style:"thin",color:BORDER};
  const headers = ["No.","Module","PB Ref","Planned","Pass","Fail","Blocked","Not Run"];
  sheet.getRange("A7:H7").values=[headers];
  sheet.getRange("A7:H7").format={fill:NAVY,font:{name:FONT,bold:true,color:"#FFFFFF"},horizontalAlignment:"center",verticalAlignment:"center",borders:{preset:"all",style:"thin",color:"#FFFFFF"},rowHeight:28};
  sprint.modules.forEach((m,idx)=>{
    const row=start+idx; const ref=sanitizeSheetRef(m.sheet);
    sheet.getRange(`A${row}:C${row}`).values=[[idx+1,m.name,m.pb]];
    sheet.getRange(`D${row}:H${row}`).formulas=[[`=${ref}!B8`,`=${ref}!B9`,`=${ref}!B10`,`=${ref}!B11`,`=${ref}!B12`]];
    if(idx%2===1) sheet.getRange(`A${row}:H${row}`).format.fill=PALE;
  });
  sheet.getRange(`A${total}:C${total}`).values=[["Total","",""]];
  sheet.getRange(`D${total}:H${total}`).formulas=[[`=SUM(D${start}:D${end})`,`=SUM(E${start}:E${end})`,`=SUM(F${start}:F${end})`,`=SUM(G${start}:G${end})`,`=SUM(H${start}:H${end})`]];
  sheet.getRange(`A${total}:H${total}`).format={fill:BLUE,font:{name:FONT,bold:true},borders:{preset:"all",style:"thin",color:BORDER}};
  sheet.getRange(`A${start}:H${end}`).format={wrapText:true,verticalAlignment:"center",borders:{preset:"all",style:"thin",color:BORDER}};
  sheet.getRange(`A${start}:A${total}`).format.horizontalAlignment="center";
  sheet.getRange(`C${start}:H${total}`).format.horizontalAlignment="center";
  sheet.getRange(`A${start}:H${end}`).format.rowHeight=42;
  sheet.getRange(`A${indicatorHeader}:B${indicatorEnd}`).values=[["Release indicators","Value"],["Execution rate",null],["Pass rate",null],["Open failures",null],["Blocked tests",null]];
  sheet.getRange(`A${indicatorHeader}:B${indicatorHeader}`).format={fill:NAVY,font:{name:FONT,bold:true,color:"#FFFFFF"},horizontalAlignment:"center",borders:{preset:"all",style:"thin",color:"#FFFFFF"}};
  sheet.getRange(`A${indicatorStart}:A${indicatorEnd}`).format={fill:BLUE,font:{name:FONT,bold:true}};
  sheet.getRange(`A${indicatorStart}:B${indicatorEnd}`).format.borders={preset:"all",style:"thin",color:BORDER};
  sheet.getRange(`B${indicatorStart}`).formulas=[[`=IF(D${total}=0,0,(D${total}-H${total})/D${total})`]];
  sheet.getRange(`B${indicatorStart+1}`).formulas=[[`=IF((D${total}-H${total})=0,0,E${total}/(D${total}-H${total}))`]];
  sheet.getRange(`B${indicatorStart+2}`).formulas=[[`=F${total}`]];
  sheet.getRange(`B${indicatorStart+3}`).formulas=[[`=G${total}`]];
  sheet.getRange(`B${indicatorStart}:B${indicatorStart+1}`).format.numberFormat="0.0%";
  [18,34,11,12,12,12,12,12].forEach((w,i)=>sheet.getRangeByIndexes(0,i,indicatorEnd,1).format.columnWidth=w);
  sheet.freezePanes.freezeRows(7);
  sheet.tabColor=NAVY;
  styleBase(sheet,`A1:H${indicatorEnd}`);
}

await fs.mkdir(PREVIEW_DIR,{recursive:true});
const manifest=[];

for (const sprint of sprints) {
  const wb=Workbook.create();
  const report=wb.worksheets.add("Sprint Report");
  for(const module of sprint.modules) wb.worksheets.add(module.sheet);
  buildReport(report,sprint);
  for(const module of sprint.modules) formatModuleSheet(wb.worksheets.getItem(module.sheet),sprint,module);
  wb.recalculate();

  const reportCheck=await wb.inspect({kind:"table",range:`'Sprint Report'!A1:H17`,include:"values,formulas",tableMaxRows:20,tableMaxCols:10,maxChars:7000});
  const errorCheck=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:100},maxChars:4000});
  const previewNames=[];
  for(const sheet of [report,...sprint.modules.map(m=>wb.worksheets.getItem(m.sheet))]){
    const rendered=await wb.render({sheetName:sheet.name,autoCrop:"all",scale:0.75,format:"png"});
    const safe=sheet.name.replaceAll(/[^A-Za-z0-9]+/g,"_");
    const p=path.join(PREVIEW_DIR,`s${sprint.no}_${safe}.png`);
    await fs.writeFile(p,new Uint8Array(await rendered.arrayBuffer()));
    previewNames.push(p);
  }
  const file=path.join(OUT_DIR,`C1SE.06_TestCase_Sprint${sprint.no}_v1.0.xlsx`);
  const blob=await SpreadsheetFile.exportXlsx(wb);
  await blob.save(file);
  manifest.push({sprint:sprint.no,file,modules:sprint.modules.length,cases:sprint.modules.reduce((n,m)=>n+m.cases.length,0),previews:previewNames,reportCheck:reportCheck.ndjson,errorCheck:errorCheck.ndjson});
}

await fs.writeFile(path.join(OUT_DIR,"build_manifest.json"),JSON.stringify(manifest,null,2),"utf8");
console.log(JSON.stringify(manifest.map(({sprint,file,modules,cases,previews,errorCheck})=>({sprint,file,modules,cases,previewCount:previews.length,errorCheck})),null,2));
