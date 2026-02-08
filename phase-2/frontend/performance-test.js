const http = require('http');

async function measurePageLoad(url) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const request = http.get(url, (response) => {
      let data = '';
      response.on('data', chunk => data += chunk);
      response.on('end', () => {
        const endTime = Date.now();
        const loadTime = endTime - startTime;
        resolve({
          statusCode: response.statusCode,
          loadTime: loadTime,
          headerSize: JSON.stringify(response.headers).length,
          contentSize: data.length,
          success: response.statusCode === 200
        });
      });
    }).on('error', reject);
  });
}

async function runPerformanceTests() {
  console.log('📊 Frontend Performance Test\n');
  console.log('Testing: http://localhost:3000\n');

  try {
    const results = [];
    for (let i = 0; i < 5; i++) {
      const result = await measurePageLoad('http://localhost:3000/');
      results.push(result);
      console.log(`Run ${i + 1}: ${result.loadTime}ms (Status: ${result.statusCode})`);
    }

    const avgLoadTime = results.reduce((a, b) => a + b.loadTime, 0) / results.length;
    const minLoadTime = Math.min(...results.map(r => r.loadTime));
    const maxLoadTime = Math.max(...results.map(r => r.loadTime));
    const allSuccess = results.every(r => r.success);

    console.log('\n📈 Results:');
    console.log(`- Average Load Time: ${avgLoadTime.toFixed(2)}ms`);
    console.log(`- Min Load Time: ${minLoadTime}ms`);
    console.log(`- Max Load Time: ${maxLoadTime}ms`);
    console.log(`- All Requests Success: ${allSuccess ? '✅ Yes' : '❌ No'}`);
    console.log(`- Target (FCP <1500ms): ${avgLoadTime < 1500 ? '✅ PASS' : '⚠️ VERIFY'}`);

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

runPerformanceTests();
