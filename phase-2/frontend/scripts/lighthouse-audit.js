/**
 * Lighthouse Accessibility Audit Script
 *
 * Runs automated accessibility audits on key pages
 * Ensures WCAG 2.1 AA compliance (target score: 90+)
 *
 * Usage:
 *   node scripts/lighthouse-audit.js
 *
 * Requirements:
 *   - Dev server must be running on http://localhost:3000
 *   - lighthouse package installed
 */

const lighthouse = require("lighthouse");
const chromeLauncher = require("chrome-launcher");
const fs = require("fs");
const path = require("path");

// Pages to audit
const PAGES_TO_AUDIT = [
  { url: "http://localhost:3000", name: "Landing Page" },
  { url: "http://localhost:3000/login", name: "Login Page" },
  { url: "http://localhost:3000/signup", name: "Signup Page" },
  // Note: Dashboard pages require authentication, test manually or with auth token
];

// Lighthouse configuration
const config = {
  extends: "lighthouse:default",
  settings: {
    onlyCategories: ["accessibility", "performance", "best-practices"],
    formFactor: "desktop",
    screenEmulation: {
      mobile: false,
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1,
    },
  },
};

// Mobile configuration
const mobileConfig = {
  extends: "lighthouse:default",
  settings: {
    onlyCategories: ["accessibility", "performance", "best-practices"],
    formFactor: "mobile",
    screenEmulation: {
      mobile: true,
      width: 375,
      height: 667,
      deviceScaleFactor: 2,
    },
  },
};

async function runAudit(url, name, isMobile = false) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless"] });
  const options = {
    logLevel: "info",
    output: "json",
    port: chrome.port,
  };

  const runnerResult = await lighthouse(
    url,
    options,
    isMobile ? mobileConfig : config
  );

  await chrome.kill();

  // Extract scores
  const { lhr } = runnerResult;
  const scores = {
    accessibility: lhr.categories.accessibility.score * 100,
    performance: lhr.categories.performance.score * 100,
    bestPractices: lhr.categories["best-practices"].score * 100,
  };

  // Accessibility audit details
  const accessibilityAudits = Object.entries(lhr.audits)
    .filter(([key, audit]) => audit.scoreDisplayMode !== "notApplicable")
    .filter(([key, audit]) => lhr.categories.accessibility.auditRefs.some((ref) => ref.id === key))
    .map(([key, audit]) => ({
      id: key,
      title: audit.title,
      score: audit.score,
      displayValue: audit.displayValue,
      description: audit.description,
    }))
    .filter((audit) => audit.score !== null && audit.score < 1);

  return { name, url, scores, accessibilityAudits, isMobile };
}

async function main() {
  console.log("🚀 Starting Lighthouse Accessibility Audit...\n");

  const results = [];

  // Test desktop
  for (const page of PAGES_TO_AUDIT) {
    console.log(`📊 Auditing ${page.name} (Desktop)...`);
    try {
      const result = await runAudit(page.url, page.name, false);
      results.push(result);
      console.log(`   ✅ Accessibility: ${result.scores.accessibility}/100`);
      console.log(`   ⚡ Performance: ${result.scores.performance}/100`);
      console.log(`   🔧 Best Practices: ${result.scores.bestPractices}/100\n`);
    } catch (error) {
      console.error(`   ❌ Error auditing ${page.name}:`, error.message);
    }
  }

  // Test mobile
  for (const page of PAGES_TO_AUDIT) {
    console.log(`📱 Auditing ${page.name} (Mobile)...`);
    try {
      const result = await runAudit(page.url, `${page.name} (Mobile)`, true);
      results.push(result);
      console.log(`   ✅ Accessibility: ${result.scores.accessibility}/100`);
      console.log(`   ⚡ Performance: ${result.scores.performance}/100`);
      console.log(`   🔧 Best Practices: ${result.scores.bestPractices}/100\n`);
    } catch (error) {
      console.error(`   ❌ Error auditing ${page.name}:`, error.message);
    }
  }

  // Generate report
  console.log("\n📝 Generating Report...\n");

  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalPages: results.length,
      averageAccessibility:
        results.reduce((sum, r) => sum + r.scores.accessibility, 0) /
        results.length,
      averagePerformance:
        results.reduce((sum, r) => sum + r.scores.performance, 0) /
        results.length,
      averageBestPractices:
        results.reduce((sum, r) => sum + r.scores.bestPractices, 0) /
        results.length,
    },
    results,
  };

  // Save report
  const reportPath = path.join(__dirname, "..", "lighthouse-report.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log("=" .repeat(60));
  console.log("📊 LIGHTHOUSE AUDIT SUMMARY");
  console.log("=" .repeat(60));
  console.log(`Total Pages Audited: ${report.summary.totalPages}`);
  console.log(
    `Average Accessibility Score: ${report.summary.averageAccessibility.toFixed(
      1
    )}/100`
  );
  console.log(
    `Average Performance Score: ${report.summary.averagePerformance.toFixed(
      1
    )}/100`
  );
  console.log(
    `Average Best Practices Score: ${report.summary.averageBestPractices.toFixed(
      1
    )}/100`
  );
  console.log("=" .repeat(60));

  // Check if accessibility goal met
  if (report.summary.averageAccessibility >= 90) {
    console.log("\n✅ SUCCESS: Accessibility score meets target (≥90)!");
  } else {
    console.log(
      "\n⚠️  WARNING: Accessibility score below target (≥90). Review issues below:\n"
    );

    results.forEach((result) => {
      if (result.accessibilityAudits.length > 0) {
        console.log(`\n${result.name} - Failed Audits:`);
        result.accessibilityAudits.forEach((audit) => {
          console.log(`  - ${audit.title}`);
          console.log(`    ${audit.description}`);
        });
      }
    });
  }

  console.log(`\n📄 Full report saved to: ${reportPath}\n`);
}

// Check if dev server is running
async function checkServer() {
  try {
    const response = await fetch("http://localhost:3000");
    if (!response.ok) {
      throw new Error("Server not responding");
    }
  } catch (error) {
    console.error("❌ Error: Dev server is not running on http://localhost:3000");
    console.error("   Please start the server with: npm run dev");
    process.exit(1);
  }
}

checkServer().then(main).catch(console.error);
