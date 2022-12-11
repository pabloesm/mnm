import { chromium } from "playwright-extra";
import minimist from "minimist";
import { parse } from "node-html-parser";
import stealth from "puppeteer-extra-plugin-stealth";
import userAgent from "user-agents";

import { upsertComments } from "./db.js";

chromium.use(stealth);

const args = minimist(process.argv.slice(2));

/*
node inspect commentsElconfidencial.js \
  --url_full=https://www.elconfidencial.com/espana/aragon/2022-11-27/espana-vaciada-partido-politico-confederado-irrumpir-congreso_3530332/ \
  --url_domain=elconfidencial.com \
  --news_id=3757998 
""*/
// Print the parsed arguments
console.log(args);

const urlFull = args.url_full;
const urlDomain = args.url_domain;
const newsId = args.news_id;

chromium
  .launch({
    headless: true,
  })
  .then(async (browser) => {
    // Create a new incognito browser context with a proper user agent
    const context = await browser.newContext({
      userAgent: userAgent.toString(),
    });

    const timeoutMs = 100000;
    context.setDefaultTimeout(timeoutMs);

    // const page = await context.newPage();

    const elConfidencial = new ElConfidencial(context);
    await elConfidencial.loadUrl(urlFull);
    const comments = await elConfidencial.getComments();
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

    const cookiesButtonText =
      "Aceptar y cerrar: Aceptar nuestro procesamiento de datos y cerrar";
    await this.page.getByRole("button", { name: cookiesButtonText }).click();

    const subscriptionButtonText = "Ahora no";
    await this.page
      .getByRole("button", { name: subscriptionButtonText })
      .click();

      await this.page.screenshot({ path: 'screenshot_loadUrl.png' });
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
    await this.page.screenshot({ path: 'screenshot_getComments.png' });
    return commentsRes;
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