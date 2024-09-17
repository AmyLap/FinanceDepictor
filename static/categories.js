// Replace 'your_file.json' with the actual path to your JSON file
const jsonFile = 'logs/categories.json';

fetch(jsonFile)
  .then(response => response.json())
  .then(jsonData => {
    // Get the keys
    const keys = Object.keys(jsonData);

    // Print the keys
    console.log('Keys:', keys);
  })
  .catch(error => console.error('Error loading JSON file:', error));
