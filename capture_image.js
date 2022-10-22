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

    try {
      const page = await browser.newPage();

      // Set Timeout to Load to 5 mins
      await page.setDefaultNavigationTimeout(300000);
      //await page.setViewport({width: 5960, height: 1000})
      //ND Mill:
      await page.goto('https://www.youtube.com/watch?v=OEvLTpOKWDM');
      //West Facing UND Cam: await page.goto('https://www.youtube.com/watch?v=mpcvRHLGBRw');
      await timeout(5000)
      await page.keyboard.press('k');
      await timeout(1000)
      await page.keyboard.press('f');
      await timeout(60000)
      await page.screenshot({path: output_file});
    } catch (e) {
      console.log(e);
    } finally {
      await browser.close();
    }
})();
