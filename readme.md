# Smart Vehicle for Vocational Training Project

This project provides an automated guidance system with facial recognition for various training and service applications. It combines Arduino modules for RFID, Bluetooth, MP3 player, and line-tracking functionalities, controlled through a Python main program on a notebook (NB) to enable facial recognition and coordinate the different functions.

## Project Overview

The system is designed to perform the following functions:

* **Guidance**: Automatically leads individuals to designated locations.
* **Joke-telling**: Plays jokes as part of user interaction.
* **Access Control**: Uses RFID for secure access.

## Directory Structure and Code Descriptions

1. **rf\_rc522**\
   Contains Arduino code for the **RFID (RC522)** module, enabling access control functions within the system.

2. **tell\_jokes**\
   This folder holds the Arduino code for **Bluetooth** and **MP3 player** functionalities, enabling the vehicle to play jokes for user interaction.

3. **tracking\_crossroads\_2**\
   Contains Arduino code for **Bluetooth** and **line-tracking** functions, facilitating movement control and guidance across paths.

4. **20241018-1.py**\
   This is the main Python program on the notebook, responsible for:

   * Facial recognition for user identification
   * Communicating with the three Arduino modules (RFID, Bluetooth/MP3, and line-tracking) to execute guidance, joke-telling, and access control functionalities

## Getting Started

### Prerequisites

* Arduino IDE for compiling and uploading code to Arduino boards.
* Python 3 for running the main program.
* Required hardware: RFID module (RC522), Bluetooth module, MP3 player, and line-tracking components.

### Setup and Usage

1. Clone this repository:

   ```
   git clone https://github.com/c8631506/smart-vehicle-for-vocational-training-project.git
   ```
2. Follow the individual setup instructions within each folder to compile and upload the Arduino code for specific functionalities.
3. Run `20241018-1.py` on the notebook to initiate the main program and control the vehicle’s features.

## License

This project is open-source and available under the MIT License.

***

This README should help clarify your project’s purpose, directory structure, and usage. Let me know if there’s any additional detail you’d like to include!

