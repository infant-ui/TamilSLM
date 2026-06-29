const { exec } = require("child_process");
const path = require("path");

async function getEnglishAnswer(query) {
    return new Promise((resolve, reject) => {

        // Path to python file
        const scriptPath = path.join(__dirname, "english1.py");

        // Run python script with query
        exec(`python "${scriptPath}" "${query}"`, (error, stdout, stderr) => {
            if (error) {
                console.error("Error:", error);
                reject("Error processing English query");
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

module.exports = { getEnglishAnswer };