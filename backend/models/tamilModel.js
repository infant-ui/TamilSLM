const { exec } = require("child_process");
const path = require("path");

async function getTamilAnswer(query) {
    return new Promise((resolve, reject) => {

        const scriptPath = path.join(__dirname, "tamil1.py");

        exec(`python "${scriptPath}" "${query}"`, (error, stdout, stderr) => {
            if (error) {
                console.error("Error:", error);
                reject("Error processing Tamil query");
            } 
            else if (stderr) {
                console.error("Stderr:", stderr);
                reject("Python error");
            } 
            else {
                resolve(stdout.trim());
            }
        });
    });
}

module.exports = { getTamilAnswer };