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
  
  export { Utils };
  