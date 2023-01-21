#!/usr/bin/nodejs

/*
Return codes:
 - 0: successfuly commented
 - 1:  

Calling example (news_id should exist in the DB to write store the data):
node inspect mnm.js \
  --username=XXXX \
  --password='YYYY' \
  --story_id=3766542 \
  --proxy_config='{"server": "XX", "username": "XX", "password": "XX"}'
  --comment="En mi opinión" 

  */

// NOTES:
// https://spys.one/en/
// https://hidemy.name/en/proxy-checker/

import { chromium } from "playwright-extra";
import minimist from "minimist";
import path from "path";
import { publicIpv4 } from "public-ip";
import stealth from "puppeteer-extra-plugin-stealth";
import userAgent from "user-agents";

import { log } from "./logger.js";
import { Utils } from "./utils.js";

chromium.use(stealth);

const scriptName = path.basename(process.argv[1]);
const args = minimist(process.argv.slice(2));

const username = args.username;
const password = args.password;
const storyId = args.story_id;
const proxyConfig = JSON.parse(args.proxy_config);
const comment = args.comment;

const args_info = {
  username: `${username[0]}+${username.length}`,
  password: `${password[0]}+${password.length}`,
  storyId: storyId,
  proxyConfig: proxyConfig,
  comment: comment,
};
log.info(args_info);

chromium
  .launch({
    headless: true,
    proxy: proxyConfig,
  })
  .then(async (browser) => {
    // Create a new incognito browser context with a proper user agent
    const context = await browser.newContext({
      userAgent: userAgent.toString(),
    });

    const timeoutMs = 100000;
    context.setDefaultTimeout(timeoutMs);

    // DO NOT catch errors here
    await ipAddressAndProxyCheck(context);

    try {
      const mnm = new Meneame(context, username, password, storyId);
      await mnm.login();
      await mnm.writeComment(comment);
      process.exitCode = 0;
    } catch (error) {
      log.error(error);
      process.exitCode = 1;
    }

    log.info(`All done in ${scriptName} ✨`);
    await browser.close();
  });

class Meneame {
  constructor(context, username, password, storyId) {
    this.context = context;
    this.username = username;
    this.password = password;
    this.storyId = storyId;
    this.url = `https://old.meneame.net/story/${storyId}`;
    this.Utils = Utils;
  }

  async login() {
    await this.loadUrl();
    await this.acceptCookies();
    await this.introduceCredentials();
  }

  async loadUrl() {
    this.page = await this.context.newPage();
    await this.page.goto(this.url);
    await this.page.screenshot({ path: `${this.username}_01_mnm_gotoUrl.png` });
  }

  async acceptCookies() {
    try {
      const cookiesPopup = await this.page.getByRole("button", {
        name: "ACEPTO",
      });
      if (cookiesPopup) {
        cookiesPopup.click();
        log.info("Cookies popup closed.");
      }
    } catch (error) {
      log.error(error);
    }
  }

  async introduceCredentials() {
    const page = this.page;

    await page.getByRole("link", { name: "login" }).click();
    await page.getByText("Usuario o Correo electrónico").click();
    await page.getByLabel("Usuario o Correo electrónico").fill(this.username);
    await page.getByLabel("Contraseña").click();
    await page.getByLabel("Contraseña").fill(this.password);
    await page.getByRole("button", { name: "Acceder" }).click();
    await this.page.screenshot({ path: `${this.username}_02_mnm_login.png` });
  }

  async writeComment(comment) {
    await this.page.waitForSelector("#footthingy");
    await this._scrollToBottom();
    const elementTextArea = await this.page.waitForSelector(
      'textarea[name="comment_content"]'
    );
    await elementTextArea.fill(comment);
    await this.page.screenshot({ path: `${this.username}_03_mnm_comment.png` });
    log.warn("Skipping 'enviar' button click.");
    // await this.page.getByText("enviar").click();
  }

  async _scrollToBottom() {
    await this.page.evaluate(this.Utils.scrollToDownSmoth);
  }
}

async function ipAddressAndProxyCheck(context) {
  const page = await context.newPage();

  const myPublicIP = await publicIpv4();
  log.info({ host_IP_address: myPublicIP });

  await page.goto("https://httpbin.org/ip");
  const ipInfoText = await page.textContent("*");
  const ipInfoJson = JSON.parse(ipInfoText);
  log.info({ proxy_IP_address: ipInfoJson["origin"] });

  if (myPublicIP === ipInfoJson["origin"]) {
    page.close();
    throw Error("IP address is not proxied");
  }

  page.close();
}
