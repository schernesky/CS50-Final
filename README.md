<h3 align="center">Leaf Me Alone: Virtual Garden</h3>

  <p align="center">
    by Sascha Chernesky
    <br />
    <a href="https://youtu.be/CHeysu_nVqY">View Video Demo</a>
  </p>
</div>

## About The Project

This website is my final project for CS50 at Yale: a virtual garden where users can grow and collect plants. I wanted to design a website where users can plan and manage their garden, select and interact with plants, and store them in a shop. I used Flask and SQL to make the functionalities of website.

## Getting Started

### Prerequisites

Running this code requires a codespace such as VSCode with Flask installed. If you do not have flask installed, you can run the following:
  ```sh
  pip install flask
  ```

Or look at this guide: https://flask.palletsprojects.com/en/stable/installation/

### Installation

First, download `garden.zip`, which contains all of the relevant html, css, py, and sql files. These pages require no additional setup, and all databases are already set up and have current user data.

Then, as I do not have my own domain, you should run the code on your own browser by running `flask run` in your terminal and opening the website when prompted.

## Usage

### Roadmap

Here is a simple roadmap to explore the main features of the website:

<ol>
    <li>Log in or Register</li>
    <li>Navigate to the <code>garden</code> page
        <ol type="a">
            <li>Select a plant</li>
            <li>Plant the seed</li>
            <li>Water the seed until it grows</li>
            <li>Harvest the plant</li>
            <li>Repeat as desired</li>
        </ol>
    </li>
    <li>Go to the <code>inventory</code> page
        <ol type="a">
            <li>Send a plant to the shop</li>
            <li>Repeat as desired</li>
        </ol>
    </li>
    <li>Look at display in the shop
        <ol type="a">
            <li>Rearrange if desired</li>
        </ol>
    </li>
    
</ol>

For experimentation and to test any additional user errors I have not caught in my code yet, you can run through different patterns of actions (e.g. trying to harvest a plant before it is grown) to see if anything causes the website to run into issues. Otherwise, you can simply continue to grow plants and made different accounts to experiment with as you go.

### List of Features

* Login and Registration
* Stored data between user sessions
* Header for navigation between pages
* Visual planter boxes
* Interactive buttons for planter boxes (plant, water, harvest)
* Multiple plant types
* Inventory of owned plants
* Visual shop for displayed plants
* Drag and drop support for shop
* Error messages
* Version number

### Future Features

* Buying and selling plants
* User interaction
* More plants
* Seeds in inventory
* More aesthetics

As this is only a preliminary outline of the website, I hope to add more error handling, additional features, and aesthetics as I spend more time developing the website. Thank you for reading and enjoy!