#!/usr/bin/nodejs

/*
Return codes:
 - 0: successfuly comments extracted and stored 
 - 1:  

Calling example (news_id should exist in the DB to write store the data):
node inspect commentsElconfidencial.js \
  --url_full=https://www.elconfidencial.com/espana/aragon/2022-11-27/espana-vaciada-partido-politico-confederado-irrumpir-congreso_3530332/ \
  --url_domain=elconfidencial.com \
  --news_id=3764927 

  
  */
import { chromium } from "playwright-extra";
import minimist from "minimist";
import { parse } from "node-html-parser";
import pRetry from "p-retry";
import { publicIpv4 } from "public-ip";
import stealth from "puppeteer-extra-plugin-stealth";
import userAgent from "user-agents";

import { upsertComments } from "./db.js";

chromium.use(stealth);

const args = minimist(process.argv.slice(2));

// Print the parsed arguments
console.log(args);

const urlFull = args.url_full;
const urlDomain = args.url_domain;
const newsId = args.news_id;

chromium
  .launch({
    headless: true,
    // proxy: {
    //   server: "188.74.183.10:8279",
    //   username: "tahdrccj",
    //   password: "phyn15nz0j3m",
    // },
  })
  .then(async (browser) => {
    // Create a new incognito browser context with a proper user agent
    const context = await browser.newContext({
      userAgent: userAgent.toString(),
    });

    const timeoutMs = 100000;
    context.setDefaultTimeout(timeoutMs);

    // const page = await context.newPage();
    const myPublicIP = await publicIpv4();
    console.log("IP address: ", myPublicIP);

    const elConfidencial = new ElConfidencial(context);
    await elConfidencial.loadUrlRetry(urlFull);
    const comments = await elConfidencial.getCommentsRetry();
    console.log(comments);

    await upsertComments(comments, newsId, urlFull);

    console.log("All done ✨");
    await browser.close();
  });

class ElConfidencial {
  constructor(context, Utils) {
    this.context = context;
    this.Utils = Utils;
  }

  async loadUrl(url) {
    this.page = await this.context.newPage();
    await this.page.goto(url);

    await this.page.screenshot({ path: `${newsId}_01_gotoUrl.png` });

    try {
      const cookiesButtonText =
        "Aceptar y cerrar: Aceptar nuestro procesamiento de datos y cerrar";
      await this.page.getByRole("button", { name: cookiesButtonText }).click();
    } catch (error) {
      console.error(error);
    }

    try {
      const subscriptionButtonText = "Ahora no";
      await this.page
        .getByRole("button", { name: subscriptionButtonText })
        .click();
    } catch (error) {
      console.error(error);
    }

    await this.page.screenshot({ path: `${newsId}_02_loadUrl.png` });
  }

  async loadUrlRetry(url) {
    await pRetry(() => this.loadUrl(url), { retries: 2 });
  }

  async getComments() {
    let commentsRes = [];

    await this._scrollToComments();
    const commentsList = await this.page.$("ec-comments-app ec-comments-list");

    // Taking only first level to avoid responses to comments
    const firstLevelComments = await commentsList.$$("div.comment");

    for (let i = 0; i < firstLevelComments.length; i++) {
      const commentContent = await firstLevelComments[i].$(
        "ec-comments-block .comment__content"
      );
      const htmlCommentContent = await commentContent.innerHTML();
      const root = parse(htmlCommentContent);

      const commentText =
        root.querySelector("div.comment__text").structuredText;
      const votesPositive = +root.querySelector(
        "div.comment__voteButton--positive span.comment__voteCounter"
      ).text;
      const votesNegative = +root.querySelector(
        "div.comment__voteButton--negative span.comment__voteCounter"
      ).text;

      const parsedComment = {
        comment: commentText,
        votes_positive: votesPositive,
        votes_negative: votesNegative,
      };

      commentsRes.push(parsedComment);
    }
    await this.page.screenshot({ path: `${newsId}_03_getComments.png` });
    return commentsRes;
  }

  async getCommentsRetry() {
    return await pRetry(() => this.getComments(), { retries: 2 });
  }

  async _scrollToComments() {
    await this.page.evaluate(Utils.scrollToDownSmoth);
  }
}

class Utils {
  static async scrollToDownSmoth() {
    // https://github.com/microsoft/playwright/issues/4302#issuecomment-1132919529
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    for (let i = 0; i < document.body.scrollHeight; i += 100) {
      window.scrollTo(0, i);
      await delay(100);
    }
  }
}
