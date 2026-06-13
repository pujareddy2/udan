const fs = require('fs');

const content = fs.readFileSync('UDAAN AI (standalone).html', 'utf8');

const startTag = '<script type="__bundler/template">';
const startIdx = content.indexOf(startTag);
if (startIdx === -1) {
  console.log("Could not find start tag");
  process.exit(1);
}

const bodyStart = startIdx + startTag.length;
const endTag = '</script>';
const endIdx = content.indexOf(endTag, bodyStart);
if (endIdx === -1) {
  console.log("Could not find end tag");
  process.exit(1);
}

const textContent = content.substring(bodyStart, endIdx);
console.log("textContent length:", textContent.length);

// Normalize newlines like a browser HTML parser does:
// The browser normalizes \r\n to \n in textContent.
const normalized = textContent.replace(/\r\n/g, '\n');
console.log("Normalized textContent length:", normalized.length);

try {
  const parsed = JSON.parse(normalized);
  console.log("Successfully parsed normalized string! Parsed length:", parsed.length);
} catch (err) {
  console.error("JSON.parse failed on normalized string:", err.message);
  const match = err.message.match(/at position (\d+)/);
  if (match) {
    const pos = parseInt(match[1]);
    console.log(`Context around error position ${pos}:`);
    console.log(JSON.stringify(normalized.substring(Math.max(0, pos - 50), Math.min(normalized.length, pos + 50))));
  }
}
