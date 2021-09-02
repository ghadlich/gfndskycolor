const puppeteer = require('puppeteer');

const output_file = process.argv[2];

function timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
};

(async() => {
    //const browser = await puppeteer.launch();

    const browser = await puppeteer.launch({
      executablePath: '/bin/google-chrome',
      headless:false, 
      defaultViewport:null,
      devtools: false,
      args: ["--window-size=1920,800"]

    })
    const page = await browser.newPage();
    //await page.setViewport({width: 5960, height: 1000})
    await page.goto('https://www.youtube.com/watch?v=OEvLTpOKWDM');
    await timeout(5000)
    await page.keyboard.press('k');
    await timeout(1000)
    await page.keyboard.press('f');
    await timeout(45000)
    await page.screenshot({path: output_file});
    browser.close();

})();
