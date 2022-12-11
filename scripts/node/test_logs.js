console.log("Starting");

const seconds = 5
const waitTill = new Date(new Date().getTime() + seconds * 1000);
while(waitTill > new Date()){}

console.log("Finishing");