#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 13:35:56 2017

@author: rsfontenot
"""
import sys
import os
sys.path.append('C:\\Users\\FontenotRS\\.spyder-py3\\Luminescence')

from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from QLed import QLed
from Light import Spectrometer as sb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyqtgraph as pg


import random
import time
import numpy as np
import pylab
import h5py
import scipy
import serial

global spec
global experimentRuns
global backgroundIntensity
global pmt

wavelength = [] #[i for i in range(1000)]
intensity = [] #[random.random() for i in range(1000)]
time_graph = []
count_graph = []


pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.title = 'Spectrometer Software'
        self.left = 100
        self.top = 100
        self.width = 1500
        self.height = 800
        self.initUI()
        
        
        
    def initUI(self):
        
        self.setStyleSheet("QPushButton {background-color: rgb(227,119,100); font: bold}")
        
        # Creating LEDs
        #Initialize Spectrometer LED
        self.SpectrometerIndicator = QLed(onColour=QLed.Green, offColour = QLed.Red, shape=QLed.Circle)
        self.SpectrometerIndicator.value = False
        # Get Data LED
        self.SingleModeIndicator = QLed(onColour=QLed.Green, offColour = QLed.Red, shape=QLed.Circle)
        self.SingleModeIndicator.value = False
        #Continuous Mode
        self.ContinuousModeIndicator = QLed(onColour=QLed.Green, offColour = QLed.Red, shape=QLed.Circle)
        self.ContinuousModeIndicator.value = False
        
        self.integrationTime = QSpinBox()
        self.integrationTime.setMinimum(1000) # 1 ms minimum
        self.integrationTime.setMaximum(10000000) # 10 s maximum
        self.integrationTime.setValue(1000000) # 1 s is default
        
        
        # Creating Buttons
        exitBtn = QPushButton('Quit')
        #exitBtn.addStretch()
        exitBtn.clicked.connect(self.close_application)
        exitBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.initSpectrometer = QPushButton('Initialize Spectrometer')
        self.initSpectrometer.setFixedWidth(150)
        self.initSpectrometer.setCheckable(True)
        #self.initSpectrometer.setStyleSheet("QPushButton {background-color: rgb(227,119,100)}")
        self.initSpectrometer.clicked.connect(self.initializeSpectrometer)
        
        self.SingleMode = QPushButton('Single Mode')
        self.SingleMode.setFixedWidth(150)
        self.ContinuousMode = QPushButton('Continuous Mode')
        self.ContinuousMode.setFixedWidth(150)
        
        
        self.setIntegrationTimeButton = QPushButton('Set Integration Time (µs)')
        self.setIntegrationTimeButton.setFixedWidth(150)
        self.setIntegrationTimeButton.clicked.connect(self.setSpecIntTime)
        
        self.directoryPath = os.getcwd()
        self.directory = QLineEdit('Save Location: '+ self.directoryPath)
        self.directory.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        

        
        # Main Layout
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        
        
        #Top layout
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.directory,10)
        topLayout.addWidget(exitBtn,1)
        
        # Middle Layout
        middleLayout = QHBoxLayout()
        

        
        
        #middleLayout.addStretch(1)

        options = QPushButton('Options')
        options.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        #Plotting section

               
        #self.graphPlot = PlotCanvas(self, width = 5, height = 4)
        #graphPlot.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        plotLayout = QVBoxLayout()
        plotLayout.setAlignment(Qt.AlignTop)
        
        
        
        
        #Options Layout
        
        optionsLayout = QVBoxLayout()
        optionsLayout.setAlignment(Qt.AlignTop)
        
        
        labelLayout = QHBoxLayout()
        specLabel = QLabel('Spectrometer \n')
        specLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 16px; color: navy}")
        labelLayout.addWidget(specLabel)
        labelLayout.addWidget(QLabel())
        
        
        step1Layout = QHBoxLayout()
        step1 = QLabel('Step 1: Initialize Spectrometer \n')
        step1.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step1Layout.addWidget(step1)
        step1Layout.addWidget(QLabel())
        
        
        initLayout = QHBoxLayout()
        initLayout.addWidget(self.SpectrometerIndicator)
        initLayout.addWidget(self.initSpectrometer)
        initLayout.setAlignment(Qt.AlignLeft)
        
        step2Layout = QHBoxLayout()
        step2 = QLabel('\n Step 2: Set the Integration Time \n')
        step2.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step2Layout.addWidget(step2)
        step2Layout.addWidget(QLabel())
        
        step3Layout = QHBoxLayout()
        step3 = QLabel('\n Step 3: Set the Acquisition Mode \n')
        step3.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step3Layout.addWidget(step3)
        step3Layout.addWidget(QLabel())
        
        step4Layout = QHBoxLayout()
        step4 = QLabel('\n Step 4: Change Save Directory (Optional) \n')
        step4.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step4Layout.addWidget(step4)
        step4Layout.addWidget(QLabel())
        
        step5Layout = QHBoxLayout()
        step5 = QLabel('\n Step 5: Begin Taking Spectra \n')
        step5.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step5Layout.addWidget(step5)
        step5Layout.addWidget(QLabel())
        
        step6Layout = QHBoxLayout()
        step6 = QLabel('\n Step 6: Set Background (Optional) \n')
        step6.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step6Layout.addWidget(step6)
        step6Layout.addWidget(QLabel())

        step7Layout = QHBoxLayout()
        step7 = QLabel('\n Step 7: Subtract Background (Optional) \n')
        step7.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step7Layout.addWidget(step7)
        step7Layout.addWidget(QLabel())      
        
        step8Layout = QHBoxLayout()
        step8 = QLabel('\n Step 8: Begin Saving \n')
        step8.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step8Layout.addWidget(step8)
        step8Layout.addWidget(QLabel())
        
        
        
        singleModeLayout = QHBoxLayout()
        singleModeLayout.addWidget(self.SingleModeIndicator)
        singleModeLayout.addWidget(self.SingleMode)
        singleModeLayout.setAlignment(Qt.AlignLeft)
        
        continuousModeLayout = QHBoxLayout()
        continuousModeLayout.addWidget(self.ContinuousModeIndicator)
        continuousModeLayout.addWidget(self.ContinuousMode)
        continuousModeLayout.setAlignment(Qt.AlignLeft)
        
        acqLayout = QVBoxLayout()
        acqLayout.setAlignment(Qt.AlignLeft)
        self.specSetting = QButtonGroup()
        self.singleAcq = QRadioButton('Single Acquisition')
        self.specSetting.addButton(self.singleAcq)
        self.continuousAcq = QRadioButton('Continuous Acquisition')
        self.continuousAcq.setChecked(True)
        self.specSetting.addButton(self.continuousAcq)
        #acqLayout.addWidget(self.singleAcq)
        acqLayout.addWidget(self.continuousAcq)
        
        #Integration Time
        integrationTimeLayout = QHBoxLayout()
        integrationTimeLayout.addWidget(self.integrationTime)
        integrationTimeLayout.addWidget(self.setIntegrationTimeButton)
        
        #Set Directory
        setDirectoryLayout = QVBoxLayout()
        setDirectoryLayout.setAlignment(Qt.AlignCenter)
        self.setDirectory = QPushButton('Set Directory')
        self.setDirectory.setFixedWidth(150)
        self.setDirectory.setCheckable(True)
        self.changeDirectory = QPushButton('Change Save Location')
        self.changeDirectory.setFixedWidth(150)
        self.changeDirectory.clicked.connect(self.newDirectory)
        self.changeDirectory.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.changeDirectory.setCheckable(False)
        setDirectoryLayout.addWidget(self.changeDirectory)
        #setDirectoryLayout.setSpacing(10)
        #setDirectoryLayout.addWidget(self.setDirectory)
        
        #Run and Stop Spectra
        self.startRun = QPushButton('Start')
        self.startRun.setFixedWidth(150)
        self.startRun.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.startRun.setCheckable(False)
        self.startRun.clicked.connect(self.plotSpectra)
        self.stopRun = QPushButton('Stop')
        self.stopRun.setFixedWidth(150)
        self.stopRun.setCheckable(True)
        self.stopRun.setStyleSheet("QPushButton {background-color: rgb(237,244,19)}")
        RunningLayout = QHBoxLayout()
        RunningLayout.setAlignment(Qt.AlignCenter)
        RunningLayout.addWidget(self.startRun)
        RunningLayout.addSpacing(8)
        RunningLayout.addWidget(self.stopRun)
        
        #Add Set Background Button

        self.setBackground = QPushButton('Set Background')
        self.setBackground.setFixedWidth(150)
        self.setBackground.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.setBackground.setCheckable(True)
        setBackgroundLayout = QHBoxLayout()
        setBackgroundLayout.setAlignment(Qt.AlignCenter)
        setBackgroundLayout.addWidget(self.setBackground)
        
        
        # Subtract background layout
        self.subtractBackground = QPushButton('Subtract Background')
        self.subtractBackground.setFixedWidth(150)
        self.subtractBackground.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.subtractBackground.setCheckable(True)
        self.undoBackground = QPushButton('Undo Background')
        self.undoBackground.setFixedWidth(150)
        self.undoBackground.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.undoBackground.setCheckable(True)
        backgroundLayout = QHBoxLayout()
        backgroundLayout.addWidget(self.subtractBackground)
        backgroundLayout.addSpacing(8)
        backgroundLayout.addWidget(self.undoBackground)
        
        
        
        #Add save button
        
        self.saveSpectraMat = QPushButton('Save as .mat')
        self.saveSpectraMat.setFixedWidth(150)
        self.saveSpectraMat.setCheckable(True)
        #self.saveSpectraTxt.setFixedHeight(60)
        #self.saveSpectraTxt.setStyleSheet("QPushButton {background-color: rgb(0,191,255)}")
        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.saveSpectraBin = QPushButton('Save as .hdf5')
        self.saveSpectraBin.setFixedWidth(150)
        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
        self.saveSpectraBin.setCheckable(True)
        #self.saveSpectraBin.clicked.connect(self.saveBinPressed)
        saveSpectralayout = QHBoxLayout()
        saveSpectralayout.setAlignment(Qt.AlignCenter)
        saveSpectralayout.addWidget(self.saveSpectraMat)
        saveSpectralayout.addSpacing(8)
        saveSpectralayout.addWidget(self.saveSpectraBin)
        
        
        
        
        optionsLayout.addLayout(labelLayout)
        optionsLayout.addLayout(step1Layout)
        optionsLayout.addLayout(initLayout)
        optionsLayout.addLayout(step2Layout)
        optionsLayout.addLayout(integrationTimeLayout)
        optionsLayout.addLayout(step3Layout)
        optionsLayout.addLayout(acqLayout)
        optionsLayout.addLayout(step4Layout)
        optionsLayout.addLayout(setDirectoryLayout)
        optionsLayout.addLayout(step5Layout)
        optionsLayout.addLayout(RunningLayout)
        optionsLayout.addLayout(step6Layout)
        optionsLayout.addLayout(setBackgroundLayout)
        optionsLayout.addLayout(step7Layout)
        optionsLayout.addLayout(backgroundLayout)
        optionsLayout.addLayout(step8Layout)
        optionsLayout.addLayout(saveSpectralayout)
        #optionsLayout.addLayout()
        
        #######################################################################
        # PMT Layout starts Here
        #######################################################################
        
        experimentLayout = QVBoxLayout()
        experimentLayout.setAlignment(Qt.AlignTop)
        
        pmtLayoutLabel = QHBoxLayout()
        pmtLabel = QLabel('PMT \n')
        pmtLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 16px; color: navy}")
        pmtLayoutLabel.addWidget(pmtLabel)
        pmtLayoutLabel.addWidget(QLabel())
        
        
        step1PMTLayout = QHBoxLayout()
        step1PMT = QLabel('Step 9: Initialize PMT \n')
        step1PMT.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        step1PMTLayout.addWidget(step1PMT)
        step1PMTLayout.addWidget(QLabel())
        
        self.PMTIndicator = QLed(onColour=QLed.Green, offColour = QLed.Red, shape=QLed.Circle)
        self.PMTIndicator.value = False
        self.initPMT = QPushButton('Initialize PMT')
        self.initPMT.setFixedWidth(150)
        self.initPMT.setCheckable(True)
        #self.initSpectrometer.setStyleSheet("QPushButton {background-color: rgb(227,119,100)}")
        self.initPMT.clicked.connect(self.initializePMT)
        
        initPMTLayout = QHBoxLayout()
        initPMTLayout.addWidget(self.PMTIndicator)
        initPMTLayout.addWidget(self.initPMT)
        initPMTLayout.setAlignment(Qt.AlignLeft)
        
        

        coolingSettingsLayout = QVBoxLayout()
        coolingSettingsLayout.setAlignment(Qt.AlignTop)
       
        coolingSettingsLabel = QHBoxLayout()
        collingLabel = QLabel('\n Laser Cooling Settings \n')
        collingLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 16px; color: navy}")
        coolingSettingsLabel.addWidget(collingLabel)
        coolingSettingsLabel.addWidget(QLabel())
        
        numOfRunsLayout = QHBoxLayout()
        step10NumOfRuns = QLabel('Step 10: Set Number of Experimental Runs \n')
        step10NumOfRuns.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        numOfRunsLayout.addWidget(step10NumOfRuns)
        numOfRunsLayout.addWidget(QLabel())
        
        setRunsLayout = QHBoxLayout()
        self.numOfRuns = QSpinBox()
        self.numOfRuns.setMinimum(1) # 1 run is minimum
        self.numOfRuns.setMaximum(100) # 100 runs is maximum
        self.numOfRuns.setValue(4) # 4 is default
        self.setNumOfRuns = QPushButton('Set Number of Runs')
        self.setNumOfRuns.setFixedWidth(150)
        self.setNumOfRuns.setCheckable(True)
        self.setNumOfRuns.clicked.connect(self.setRunNumber)
        setRunsLayout.addWidget(self.numOfRuns)
        setRunsLayout.addWidget(self.setNumOfRuns)
        
        coolingTimeLayout = QHBoxLayout()
        cTimeLabel = QLabel('\n Step 11: Set Cooling Time (min) \n')
        cTimeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        coolingTimeLayout.addWidget(cTimeLabel)
        coolingTimeLayout.addWidget(QLabel())
        
        setCoolingTimeLayout = QHBoxLayout()
        self.cTime = QSpinBox()
        self.cTime.setMinimum(1) # 1 min is minimum
        self.cTime.setMaximum(240) # 240 min is maximum
        self.cTime.setValue(30) # 30 min is default
        self.setCTime = QPushButton('Set Cooling Time')
        self.setCTime.setFixedWidth(150)
        self.setCTime.setCheckable(True)
        self.setCTime.clicked.connect(self.setCoolingTime)
        setCoolingTimeLayout.addWidget(self.cTime)
        setCoolingTimeLayout.addWidget(self.setCTime)
        
        PLTimeLayout = QHBoxLayout()
        PLTimeLabel = QLabel('\n Step 12: Set PL Time (min) \n')
        PLTimeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        PLTimeLayout.addWidget(PLTimeLabel)
        PLTimeLayout.addWidget(QLabel())
        setPLTimeLayout = QHBoxLayout()
        self.PLTime = QSpinBox()
        self.PLTime.setMinimum(1) # 1 min is minimum
        self.PLTime.setMaximum(120) # 120 min is the maximum
        self.PLTime.setValue(20) # 20 minutes is default
        self.setPLTime = QPushButton('Set PL Time')
        self.setPLTime.setFixedWidth(150)
        self.setPLTime.setCheckable(True)
        self.setPLTime.clicked.connect(self.set_PL_Time)
        setPLTimeLayout.addWidget(self.PLTime)
        setPLTimeLayout.addWidget(self.setPLTime)
        
        equilibriumLayout = QHBoxLayout()
        equilibriumLabel = QLabel('\n Step 13: Set Equilibrium Time between Runs (min) \n')
        equilibriumLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        equilibriumLayout.addWidget(equilibriumLabel)
        equilibriumLayout.addWidget(QLabel())
        setEqTimeLayout = QHBoxLayout()
        self.eqTime = QSpinBox()
        self.eqTime.setMinimum(1) # 1 min is minimum
        self.eqTime.setMaximum(500) # 500 min is the maximum
        self.eqTime.setValue(120) # 120 minutes is default
        self.setEqTime = QPushButton('Set Equilibrium Time')
        self.setEqTime.setFixedWidth(150)
        self.setEqTime.setCheckable(True)
        self.setEqTime.clicked.connect(self.set_eq_Time)
        setEqTimeLayout.addWidget(self.eqTime)
        setEqTimeLayout.addWidget(self.setEqTime)
        
        startLayout = QHBoxLayout()
        startLabel = QLabel('\n Step 14: Set Time for Laser to reach equilibrium (min) \n')
        startLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        startLayout.addWidget(startLabel)
        startLayout.addWidget(QLabel())
        setLaserTimeLayout = QHBoxLayout()
        self.laserTime = QSpinBox()
        self.laserTime.setMinimum(0) # 0 min is minimum
        self.laserTime.setMaximum(500) # 500 min is the maximum
        self.laserTime.setValue(120) # 120 minutes is default
        self.setlaserTime = QPushButton('Set Laser Equilibrium Time')
        self.setlaserTime.setFixedWidth(150)
        self.setlaserTime.setCheckable(True)
        self.setlaserTime.clicked.connect(self.set_laser_Time)
        setLaserTimeLayout.addWidget(self.laserTime)
        setLaserTimeLayout.addWidget(self.setlaserTime)
        
        shutterLayout = QHBoxLayout()
        shutterLayout.setAlignment(Qt.AlignLeft)
        shutterLabel = QLabel('\n Step 15: Enable Shutters \n')
        shutterLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        shutterButtonLayout = QHBoxLayout()
        shutterButtonLayout.setAlignment(Qt.AlignCenter)
        self.shutterButton = QPushButton('Enable Shutters')
        self.shutterButton.setFixedWidth(200)
        self.shutterButton.setFixedHeight(40)
        self.shutterButton.setCheckable(True)
        self.shutterButton.clicked.connect(self.enable_shutters)
        shutterLayout.addWidget(shutterLabel)
        shutterLayout.addWidget(QLabel())
        shutterButtonLayout.addWidget(self.shutterButton)
        #shutterLayout.addWidget(self.shutterButton)
        
        startExperimentLayout = QHBoxLayout()
        startExpLabel = QLabel('\n Step 16: Start Cooling Experiment \n')
        startExpLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 14px; color: black}")
        startExperimentLayout.addWidget(startExpLabel)
        startExperimentLayout.addWidget(QLabel())
        startButtonLayout = QHBoxLayout()
        self.startTheExperiment= QPushButton('Begin Cooling Experiment')
        self.startTheExperiment.setFixedWidth(300)
        self.startTheExperiment.setFixedHeight(50)
        self.startTheExperiment.setCheckable(True)
        self.startTheExperiment.clicked.connect(self.beginCooling)
        startButtonLayout.addWidget(self.startTheExperiment)
        
        
        
        
        experimentLayout.addLayout(pmtLayoutLabel)
        experimentLayout.addLayout(step1PMTLayout)
        experimentLayout.addLayout(initPMTLayout)
        experimentLayout.addLayout(coolingSettingsLayout)
        experimentLayout.addLayout(coolingSettingsLabel)
        experimentLayout.addLayout(numOfRunsLayout)
        experimentLayout.addLayout(setRunsLayout)
        experimentLayout.addLayout(coolingTimeLayout)
        experimentLayout.addLayout(setCoolingTimeLayout)
        experimentLayout.addLayout(PLTimeLayout)
        experimentLayout.addLayout(setPLTimeLayout)
        experimentLayout.addLayout(equilibriumLayout)
        experimentLayout.addLayout(setEqTimeLayout)
        experimentLayout.addLayout(startLayout)
        experimentLayout.addLayout(setLaserTimeLayout)
        experimentLayout.addLayout(shutterLayout)
        experimentLayout.addLayout(shutterButtonLayout)
        experimentLayout.addLayout(startExperimentLayout)
        experimentLayout.addLayout(startButtonLayout)
        
        
        #Plotting Section
        
        topPlotLayout = QHBoxLayout()
        self.PLPlot = pg.PlotWidget(name = 'Luminescence Spectrum')
        self.PLPlot.setLabel('bottom', 'Wavelength (nm)')
        self.PLPlot.setLabel('left', 'Intensity')
        self.PLPlot.setLabel('top', 'Laser Spectrum')
        self.luminescencePlot = self.PLPlot.plot(wavelength, intensity)
        self.luminescencePlot.setPen((0,0,0))
        #self.luminescencePlot.setLable('bottom', 'Wavelength (nm)')
        
        self.countsPlot = pg.PlotWidget(name = 'Count Plot')
        self.countsPlot.setLabel('bottom', 'Elapsed time', units = 's')
        self.countsPlot.setLabel('left', 'Normalized Counts')
        self.countsPlot.setLabel('top', 'Counts')
        self.normalizedCountsPlot = self.countsPlot.plot(time_graph, count_graph)
        self.normalizedCountsPlot.setPen((0,0,0))        
        
        
        topPlotLayout.addWidget(self.PLPlot)
        topPlotLayout.addWidget(self.countsPlot)
        
        bottomPlotLayout = QHBoxLayout()
        bottomStatusLayout = QVBoxLayout()
        bottomStatusLayout.setAlignment(Qt.AlignTop)
        self.statusLabel = QLabel('\n Cooling Experiment Status')
        self.statusLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 36px; color: navy}")
        minLayout = QHBoxLayout()
        minLayout.setAlignment(Qt.AlignHCenter)
        self.typeLabel = QLabel('Laser Equilibrium: ')
        self.typeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
        self.minutesRemaining = QLCDNumber()
        self.minutesRemaining.display(self.laserTime.value())
        self.minutesRemaining.setStyleSheet("QLCDNumber {border: none; color: red; font-family: 'Times New Roman'; font-size: 24px; }")
        minText = QLabel('min remaining')
        minText.setAlignment(Qt.AlignHCenter)
        minText.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
        minText.setAlignment(Qt.AlignLeft)
        
        minLayout.addWidget(self.typeLabel)
        minLayout.addWidget(self.minutesRemaining)
        minLayout.addWidget(minText)
        
        #defaultLabel = QLabel('Laser Equilibrium Mode: ' + str(self.laserTime.value()) + ' minutes remaining')
        #defaultLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
        bottomStatusLayout.addWidget(self.statusLabel)
        bottomStatusLayout.addWidget(QLabel())
        #bottomStatusLayout.addWidget(self.typeLabel)
        #bottomStatusLayout.addWidget(QLabel())
        bottomStatusLayout.addLayout(minLayout)
        
        runRemainingLayout = QVBoxLayout()
        self.runLabel = QLabel('\n Current Experiment ')
        self.runLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 36px; color: navy}")
        runRemainingLayout.addWidget(self.runLabel)
        runRemainingLayout.addWidget(QLabel())
        runRemainingLayout.setAlignment(Qt.AlignTop)
        runLayout = QHBoxLayout()
        runLayout.setAlignment(Qt.AlignHCenter)
        runLayout.setAlignment(Qt.AlignTop)
        runlabel = QLabel('Run ')
        runlabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
        self.runLCD = QLCDNumber()
        self.runLCD.display(0)
        self.runLCD.setStyleSheet("QLCDNumber {border: none; color: black; font-family: 'Times New Roman'; font-size: 24px; }")
        self.runLCD.setSegmentStyle(QLCDNumber.Flat)
        ofLabel = QLabel(' of ')
        ofLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
        self.runTotalLCD = QLCDNumber()
        self.runTotalLCD.setStyleSheet("QLCDNumber {border: none; color: black; font-family: 'Times New Roman'; font-size: 24px; }")
        self.runTotalLCD.display(self.numOfRuns.value())
        blankLabel = QLabel('\n \n \n \n \n \n ')
        
        runLayout.addWidget(runlabel)
        runLayout.addWidget(QLabel())
        runLayout.addWidget(self.runLCD)
        runLayout.addWidget(ofLabel)
        runLayout.addWidget(QLabel())
        runLayout.addWidget(self.runTotalLCD)
        runLayout.addWidget(blankLabel)
        runLayout.addWidget(QLabel())
        
        runRemainingLayout.addLayout(runLayout)

        
        bottomPlotLayout.addLayout(bottomStatusLayout)
        bottomPlotLayout.addSpacing(26)
        bottomPlotLayout.addLayout(runRemainingLayout)
        plotLayout.addLayout(topPlotLayout)
        plotLayout.addLayout(bottomPlotLayout)
        
        
        #Putting middle layout together
        
        #middleLayout.addLayout(labelLayout)
        middleLayout.addLayout(optionsLayout)
        middleLayout.addSpacing(12)
        middleLayout.addLayout(experimentLayout)
        middleLayout.addSpacing(12)
        #middleLayout.addWidget(options,2)
        middleLayout.addLayout(plotLayout)
        
        #Bottom Layout
        bottomLayout = QHBoxLayout()
        self.outputMessages = QLineEdit()
        self.outputMessages.setObjectName("outputMessages")
        self.outputMessages.setText("Output Messages")
        self.outputMessages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.progressBar = QProgressBar()
        self.progressBar.resize(120,100)
        self.progressBar.setValue(0)
        #progressBar.setMinimumWidth(200)
        #progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bottomLayout.addWidget(self.outputMessages,8)
        bottomLayout.addWidget(self.progressBar)
        
       
        
        
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(middleLayout)
        mainLayout.addLayout(bottomLayout)
        
        self.setLayout(mainLayout)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.move(50,20)
        self.show()

        


    def close_application(self):
        self.outputMessages.setText("Program is closing")
        time.sleep(2) #This pauses the program for 3 seconds
        sys.exit()
        
        
    def initializeSpectrometer(self):
                       
        if self.SpectrometerIndicator.value == False:
            self.outputMessages.setText("Spectrometer is initializing")
            self.spec = sb.initalizeOceanOptics() #Establishes communication with the spectrometer
            for x in range(1,5):
                time.sleep(0.5)
                self.progressBar.setValue(x/4*100)
            self.SpectrometerIndicator.value = True
            self.outputMessages.setText("Spectrometer is ready to go")
            self.initSpectrometer.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
            return self.spec
        else:
            self.outputMessages.setText("Spectrometer is disconnecting")
            sb.closeSpectrometer(self.spec)
            for x in range(1,5):
                time.sleep(0.5)
                self.progressBar.setValue(x/4*100)
            self.SpectrometerIndicator.value = False #Closes the spectrometer
            self.outputMessages.setText("Spectrometer has been disconnected")
            self.initSpectrometer.setStyleSheet("QPushButton {background-color: rgb(227,119,100)}")
            
    def setSpecIntTime(self):
        #time = self.integrationTime.value()
        time = 800000 #800 ms integration, 200 ms for processing/saving data
        #for x in range(1,4):
            #time.sleep(0.5)
            #self.progressBar.setValue(x/3*100)
        sb.setIntegrationTime(time)
        self.outputMessages.setText("Integration time has been set to "+ str(time/1000) + " ms")
        self.setIntegrationTimeButton.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
       
        
    def newDirectory(self):
        self.directoryPath = QFileDialog.getExistingDirectory(self,"Choose a Directory to Save the data")
        self.directory.setText('Save Location: '+ self.directoryPath)
        return self.directoryPath

    
    def plotSpectra(self):
        global backgroundIntensity
        t = self.integrationTime.value()
        x=1
        checked = False
        if self.singleAcq.isChecked():
            print("Im in single mode")
            wavelength = sb.getWavelength()
            intensity = sb.getIntensity()
            pg.QtGui.QApplication.processEvents()
            print("Interation : " + str(x))
            self.outputMessages.setText("Spectrum " + str(x))
            self.luminescencePlot = self.PLPlot.plot(wavelength, intensity, clear = True, pen = pg.mkPen('r'))
            font = QFont('Times New Roman', 12)
            labelStyle = {'color': 'k', 'font-size': '10pt'}
            self.PLPlot.setLabel('bottom', text = 'Wavelength (nm)', **labelStyle)
            self.PLPlot.setLabel('left', text = 'Intensity (a.u.)',**labelStyle)
            time.sleep(t/1000000)
        else:
            while self.stopRun.isChecked() == False:
                if self.setBackground.isChecked():
                    #print('Background set button is pressed')
                    wavelength = sb.getWavelength()
                    backgroundIntensity = sb.getIntensity()
                    intensity = backgroundIntensity 
                    x = x+1
                    pg.QtGui.QApplication.processEvents()
                    self.outputMessages.setText("Background spectrum has been set")
                    self.setBackground.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    time.sleep(t/1000000)
                    self.setBackground.setChecked(False)
                    
                    
                if self.subtractBackground.isChecked():
                    checked = True
                    self.subtractBackground.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    self.subtractBackground.setChecked(False)
                    if self.saveSpectraBin.isChecked():
                        name = os.path.join(self.directoryPath,'BackgroundSpectrum.h5')
                        f = h5py.File(name, "w")
                        f.create_dataset('Background Subtracted', data=True)
                        f.create_dataset('Wavelength', data=wavelength)
                        f.create_dataset('Intensity', data=intensity)
                        f.close()
                        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    else:
                        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                    
                    if self.saveSpectraMat.isChecked():
                        name = os.path.join(self.directoryPath,'BackgroundSpectrum')
                        data = {'Background Subtraction': True,
                                'Wavelength': wavelength,
                                'Intensity': intensity}
                        scipy.io.savemat(name, mdict=data, appendmat = True)
                        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    else:
                        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                        
                
                if self.undoBackground.isChecked() == True:
                    checked = False
                    self.subtractBackground.setChecked(False)
                    self.subtractBackground.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                    self.undoBackground.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                    self.undoBackground.setChecked(False)
                
                if checked:
                    wavelength = sb.getWavelength()
                    rawIntensity = sb.getIntensity()
                    intensity = rawIntensity - backgroundIntensity
                    if self.saveSpectraBin.isChecked():
                        name = os.path.join(self.directoryPath, 'Spectrum'+str(x)+'_Background_subtracted.h5')
                        f = h5py.File(name, "w")
                        f.create_dataset(name, data=True)
                        f.create_dataset('Wavelength', data=wavelength)
                        f.create_dataset('Intensity', data=intensity)
                        f.close()
                        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    else:
                        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                        
                    if self.saveSpectraMat.isChecked():
                        name = os.path.join(self.directoryPath,'Spectrum'+str(x)+'_Background_subtracted')
                        data = {'Background Subtraction': True,
                                'Wavelength': wavelength,
                                'Intensity': intensity}
                        scipy.io.savemat(name, mdict=data, appendmat = True)
                        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    else:
                        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                else:
                    wavelength = sb.getWavelength()
                    intensity = sb.getIntensity()
                    if self.saveSpectraBin.isChecked():
                        name = os.path.join(self.directoryPath, 'Spectrum'+str(x)+'_No_Background.h5')
                        f = h5py.File(name, "w")
                        f.create_dataset(name, data=False)
                        f.create_dataset('Wavelength', data=wavelength)
                        f.create_dataset('Intensity', data=intensity)
                        f.close()
                        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    else:
                        self.saveSpectraBin.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")
                        
                    if self.saveSpectraMat.isChecked():
                        name = os.path.join(self.directoryPath,'Spectrum'+str(x)+'_No_Background')
                        data = {'Background Subtraction': True,
                                'Wavelength': wavelength,
                                'Intensity': intensity}
                        scipy.io.savemat(name, mdict=data, appendmat = True)
                        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
                    else:
                        self.saveSpectraMat.setStyleSheet("QPushButton {background-color: rgb(255,255,255)}")                    
    
                pg.QtGui.QApplication.processEvents()
                #print("Interation : " + str(x))
                #self.outputMessages.setText("Spectrum " + str(x))
                self.luminescencePlot = self.PLPlot.plot(wavelength, intensity, clear = True, pen = pg.mkPen('r'))
                font = QFont('Times New Roman', 12)
                labelStyle = {'color': 'k', 'font-size': '10pt'}
                self.PLPlot.setLabel('bottom', text = 'Wavelength (nm)', **labelStyle)
                self.PLPlot.setLabel('left', text = 'Intensity (a.u.)',**labelStyle)
                #self.graphPlot.getAxis('bottom').labelFont = font
                #self.graphPlot.getAxis('left').labelFont = font
                time.sleep(t/1000000)
                x = x+1
            #self.graphPlot.clear()
            
            #if self.stopRun.isChecked()== True:
                #self.outputMessages.setText("Data collection has ceased")
                #break
    
    
    def initializePMT(self):
        global pmt 
        
        pmt = serial.Serial()
        pmt.baudrate = 9600
        pmt.port = 'COM9'
        pmt.parity = serial.PARITY_NONE
        pmt.stopbits = serial.STOPBITS_ONE
        pmt.timeout = 1 #1 s timeout
        pmt.bytesize =  serial.EIGHTBITS
        pmt.open()

        #Setting the voltage to default 
        pmt.write(bytes(b'D\r'))
        pmt.read(100)
        time.sleep(0.5)
        #Set it to one reading per run
        pmt.write(bytes(b'R1\r'))
        pmt.read(100)

        time.sleep(0.5)

        #Set it to 1 s integration time
        # hex(100) = 64
        pmt.write(bytes(b'\x50\x50\x0D')) #800 ms integration time
        pmt.read(100)
        time.sleep(0.5)
        self.PMTIndicator.value = True
        self.outputMessages.setText("PMT has been initialized")
        self.initPMT.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        
    
    def setRunNumber(self):
        experimentRuns = self.numOfRuns.value()
        self.numOfRuns.setEnabled(False)
        self.setNumOfRuns.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.setNumOfRuns.setEnabled(False)
        self.runTotalLCD.display(self.numOfRuns.value())
        self.outputMessages.setText("Number of Runs have been set to " + str(experimentRuns))
        
    
    def setCoolingTime(self):
        self.setCTime.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.cTime.setEnabled(False)
        self.setCTime.setEnabled(False)
        self.outputMessages.setText('The Cooling time has been set to ' + str(self.cTime.value())+ ' min.')
        
    
    def set_PL_Time(self):
        self.setPLTime.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.PLTime.setEnabled(False)
        self.setPLTime.setEnabled(False)
        self.outputMessages.setText('The PL time has been set to ' + str(self.PLTime.value())+ ' min.')
        
    
    def set_eq_Time(self):
        self.setEqTime.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.eqTime.setEnabled(False)
        self.setEqTime.setEnabled(False)
        self.outputMessages.setText('The equilibrium time between experimental runs has been set to ' + str(self.eqTime.value())+ ' min.')

    
    def set_laser_Time(self):
        self.laserTime.setEnabled(False)
        self.setlaserTime.setEnabled(False)
        self.setlaserTime.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.outputMessages.setText('The laser equilibrium time has been set to ' + str(self.laserTime.value())+ ' min.')
        
    def enable_shutters(self):
        self.shutterButton.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.shutterButton.setEnabled(False)
        
        #Connecting to the cooling shutter
        self.CoolingShutter = serial.Serial()
        self.CoolingShutter.baudrate = 9600
        self.CoolingShutter.port = 'COM5'
        self.CoolingShutter.parity = serial.PARITY_NONE
        self.CoolingShutter.stopbits = serial.STOPBITS_ONE
        self.CoolingShutter.timeout = 1 #1 s timeout
        self.CoolingShutter.open()
        
        self.PLShutter = serial.Serial()
        self.PLShutter.baudrate = 9600
        self.PLShutter.port = 'COM4'
        self.PLShutter.parity = serial.PARITY_NONE
        self.PLShutter.stopbits = serial.STOPBITS_ONE
        self.PLShutter.timeout = 1 #1 s timeout
        self.PLShutter.open()

        if not self.CoolingShutter.is_open:
            print('Error: Cannot Connect to the cooling shutter')
            
        if not self.PLShutter.is_open:
            print('Error: Cannot Connect to the PL shutter')
        
        #Step 1: Clear the buffer, ans should say 'Command error CMD_NOT_DEFINED

        self.CoolingShutter.write(bytes(b"\r"))
        self.CoolingShutter.read(size = 100)
        self.PLShutter.write(bytes(b"\r"))
        self.PLShutter.read(size = 100)
        
        #Step 2: Set the operating mode to manual
        self.CoolingShutter.write(bytes(b"mode=1\r"))
        self.CoolingShutter.read(size = 100)
        self.PLShutter.write(bytes(b"mode=1\r"))
        self.PLShutter.read(size = 100)
        
        #Step 3: Close the Shutter
        self.CoolingShutter.write(bytes(b"ens\r"))
        self.CoolingShutter.read(size = 100)
        self.PLShutter.write(bytes(b"ens\r"))
        self.PLShutter.read(size = 100)       
        
        #Check to see if the Shutter is Open
        self.CoolingShutter.write(bytes(b"ens?\r"))
        ans = self.CoolingShutter.read(size = 100)
        print(ans)
        QApplication.processEvents()
        
        if b'1' in ans:
            self.CoolingShutter.write(bytes(b"ens\r"))
            self.CoolingShutter.read(size = 100)
            time.sleep(1)
        
        ans = self.CoolingShutter.read(size = 100)
        if b'1' in ans:
            print('Error: Cannot Close Cooling Shutter')
            sys.exit(app.exec_())
        
        QApplication.processEvents()
        
        #Check to see if the Shutter is Open
        self.PLShutter.write(bytes(b"ens?\r"))
        ans = self.PLShutter.read(size = 100)
        
        if b'1' in ans:
            self.PLShutter.write(bytes(b"ens\r"))
            time.sleep(1)
        
        ans = self.PLShutter.read(size = 100)
        if b'1' in ans:
            print('Error: Cannot Close PL Shutter')
            sys.exit(app.exec_())
    
        self.outputMessages.setText('Shutters are now connected and closed.')
        
    def beginCooling(self):
        
        
        #Step 1: Diable all buttons so no more changes can occur once experiment starts
        self.startTheExperiment.setStyleSheet("QPushButton {background-color: rgb(85,225,0)}")
        self.startTheExperiment.setEnabled(False)
        self.initSpectrometer.setEnabled(False)
        self.setIntegrationTimeButton.setEnabled(False)
        self.setDirectory.setEnabled(False)
        self.changeDirectory.setEnabled(False)
        self.startRun.setEnabled(False)
        self.stopRun.setEnabled(False)
        self.setBackground.setEnabled(False)
        self.subtractBackground.setEnabled(False)
        self.undoBackground.setEnabled(False)
        self.saveSpectraMat.setEnabled(False)
        self.saveSpectraBin.setEnabled(False)
        self.initPMT.setEnabled(False)
        QApplication.processEvents()
        
            
        #Step 2: Begin the Cooling Experiment 
        self.outputMessages.setText('First run of the day. Laser is reaching equilibrium.')
        
        for x in range(self.laserTime.value()*60,0,-1):
            self.minutesRemaining.display(x/60)
            time.sleep(1) #Change all of these to 1 s
            #self.outputMessages.setText(str(x/60) + ' min remaining')
            QApplication.processEvents() #This is required to refresh the GUI
        
        
        #Step 3: Start the Number of Runs loop
        
        
        for x in range(1,self.numOfRuns.value()+1,1):
            
            self.runLCD.display(x)
            
        
            self.typeLabel.setText('Room Temperature PL Spectrum: ')
            self.typeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
            QApplication.processEvents()
            
            #Step 3: Open the PL Shutters
            self.PLShutter.write(bytes(b"ens\r"))
            self.PLShutter.read(size = 100)
            time.sleep(1)
            
            self.PLShutter.write(bytes(b"ens?\r"))
            ans = self.PLShutter.read(size = 100)
            if b'0' in ans:
                self.PLShutter.write(bytes(b"ens\r"))
                self.PLShutter.read(size = 100)
                time.sleep(1)
                
            ans = self.PLShutter.read(size = 100)
            if b'0' in ans:
                print('Error: Cannot Open PL Shutter')
                sys.exit(app.exec_())
            
            #Create the run folder
            
            runString = 'Run '+str(x)
            fullRunPath = os.path.join(self.directoryPath, runString)
            
            if not os.path.exists(fullRunPath):
                os.mkdir(fullRunPath)
            
            #Creating variable arrays
            startTime = time.time()
            time_graph = []
            count_graph = []
            allCounts = []
            areaCurve = []
            normalizedCounts = []
            maxIntensities = []
            spectrum_array = []
            
            RTfullRunPath = os.path.join(self.directoryPath, runString, 'RT')
            if not os.path.exists(RTfullRunPath):
                os.mkdir(RTfullRunPath)
            
            #Step 5: Start the RT PL measurements
            for y in range(self.PLTime.value()*60,0,-1):
                loopStartTime = time.time()
                self.minutesRemaining.display(y/60)
                #Get the laser spectrum
                pmt.write(bytes(B'S\r'))
                wavelength = sb.getWavelength()
                rawIntensity = sb.getIntensity()
                intensity = rawIntensity - backgroundIntensity
                
                #Get the PMT Counts
                
                
                try:
                    sol = pmt.read(400) #this reads the 4 bytes of data
                    time.sleep(0.01)
                    counts = sol[0]*16777216+sol[1]*65536+sol[2]*256+sol[3]
                except IndexError:
                    counts = 0
                    pass
                    
                #processStart = time.time()
                #Correcting the Data                
                PLWavelength = wavelength[(wavelength>=508) & (wavelength <= 522)]
                PLIntensity = intensity[(wavelength>=508) & (wavelength <= 522)]
                
                #Getting the background
                PLBackground = np.mean(intensity[(wavelength>=430) & (wavelength <= 480)])
                #Normalized Intenisty
                
                PLIntenistyBackgroundCorrected = PLIntensity-PLBackground
                #Area Under the Curve (total light emitted)
                areaUnderCurve = np.trapz(PLIntenistyBackgroundCorrected, x = PLWavelength)
                
                maxIntensity = np.max(PLIntenistyBackgroundCorrected)
                normalized_Counts = counts/areaUnderCurve*1000
                
                #processEnd = time.time()-processStart
                #print('the total time for processing the data is: ', processEnd)
                
                elapsedTime = time.time()-startTime
                #time_graph.append(elapsedTime)
                #count_graph.append(counts)
                
                #Saving the data
                runStr = 'RTSpectrumAndCounts'+str(y)+'ofRun' + str(x) + '.h5'
                name = os.path.join(RTfullRunPath, runStr)
                f = h5py.File(name, "w")
                f.create_dataset(name, data=True)
                f.create_dataset('Time', data = elapsedTime)
                f.create_dataset('Spectrum', data = y)
                f.create_dataset('Wavelength', data = wavelength)
                f.create_dataset('Intensity', data = intensity)
                f.create_dataset('Analyzed Wavelength', data = PLWavelength)
                f.create_dataset('Background Corrected Intensity', data = PLIntenistyBackgroundCorrected)
                f.create_dataset('Counts', data = counts)
                f.create_dataset('Area Under Curve', data = areaUnderCurve)
                f.create_dataset('Normalized Counts', data = normalized_Counts)
                f.create_dataset('Max Intensity', data = maxIntensity)
                f.close()
                
                #Saving the Data
                spectrum_array.append(y)
                time_graph.append(elapsedTime)
                count_graph.append(counts)
                areaCurve.append(areaUnderCurve)
                maxIntensities.append(maxIntensity)
                normalizedCounts.append(normalized_Counts)
                
                #Plot the Data
                self.luminescencePlot = self.PLPlot.plot(wavelength, intensity, clear = True, pen = pg.mkPen('r'))
                self.luminescencePlot.setPen((0,0,0))
                font = QFont('Times New Roman', 12)
                labelStyle = {'color': 'k', 'font-size': '10pt'}
                self.PLPlot.setLabel('bottom', text = 'Wavelength (nm)', **labelStyle)
                self.PLPlot.setLabel('left', text = 'Intensity (a.u.)',**labelStyle)
                self.PLPlot.setLabel('top', 'Laser Spectrum',**labelStyle)
                
                #Plot the Counts
        
                self.normalizedCountsPlot = self.countsPlot.plot(time_graph, count_graph)
                self.normalizedCountsPlot.setPen((0,0,0))
                font = QFont('Times New Roman', 12)
                labelStyle = {'color': 'k', 'font-size': '10pt'}
                self.countsPlot.setLabel('bottom', text = 'Elapsed Time (s)',**labelStyle)
                self.countsPlot.setLabel('left', text = 'Counts', **labelStyle)
                self.countsPlot.setLabel('top', 'PMT Counts')
                
                #Counts Plot 
                QApplication.processEvents()
                
                timeRemaining = 1-(time.time()-loopStartTime)
                
                if timeRemaining > 0:
                    time.sleep(timeRemaining)

            #Save the PL RT Measurements to one file
            RunDataname = os.path.join(RTfullRunPath, 'RT Run ' +  str(x) + ' Data.h5')
            f2 = h5py.File(RunDataname, "w")
            f2.create_dataset(RunDataname, data=True)
            f2.create_dataset('Elasped Time', data = time_graph)
            f2.create_dataset('Spectrum', data = spectrum_array)
            f2.create_dataset('Counts', data = count_graph)
            f2.create_dataset('Area Under Curve', data = areaCurve)
            f2.create_dataset('Max Intensity', data = maxIntensities)
            f2.create_dataset('Normalized Counts', data = normalizedCounts)
            f2.close()
            
            #Set the cooling time
            self.typeLabel.setText('Cooling Time Remaining (min): ')
            self.typeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
            QApplication.processEvents()
            
            #Step 6: Close the PL Shutters
            
            self.PLShutter.write(bytes(b"ens\r"))
            self.PLShutter.read(size = 100)
            time.sleep(1)
            
            self.PLShutter.write(bytes(b"ens?\r"))
            ans = self.PLShutter.read(size = 100)
            if b'1' in ans:
                self.PLShutter.write(bytes(b"ens\r"))
                self.PLShutter.read(size = 100)
                time.sleep(1)
                
            ans = self.PLShutter.read(size = 100)
            if b'1' in ans:
                print('Error: Cannot Open PL Shutter')
                sys.exit(app.exec_())
            
            #Step 7: Open the Cooling Shutters
           
            self.CoolingShutter.write(bytes(b"\r"))
            self.CoolingShutter.read(size = 100)
            
            self.CoolingShutter.write(bytes(b"ens?\r"))
            ans = self.CoolingShutter.read(size = 100)
            if b'0' in ans:
                self.CoolingShutter.write(bytes(b"ens\r"))
                self.CoolingShutter.read(size = 100)
                time.sleep(1)
                
            ans = self.CoolingShutter.read(size = 100)
            if b'0' in ans:
                print('Error: Cannot Open Cooling Shutter')
                sys.exit(app.exec_())
                        
            
            #Step 8: Let Cooling Occur
            for a in range(self.cTime.value()*60,0,-1):
                self.minutesRemaining.display(a/60)
                time.sleep(1)
                QApplication.processEvents()
                
            #Step 9: Close the Shutters
           
            self.CoolingShutter.write(bytes(b"\r"))
            self.CoolingShutter.read(size = 100)
            
            self.CoolingShutter.write(bytes(b"ens?\r"))
            ans = self.CoolingShutter.read(size = 100)
            if b'1' in ans:
                self.CoolingShutter.write(bytes(b"ens\r"))
                self.CoolingShutter.read(size = 100)
                time.sleep(1)
                
            ans = self.CoolingShutter.read(size = 100)
            if b'1' in ans:
                print('Error: Cannot Close Cooling Shutter')
                sys.exit(app.exec_())
                
            
            #Step 10: Open the PL Shutters 
            self.PLShutter.write(bytes(b"ens\r"))
            self.PLShutter.read(size = 100)
            time.sleep(1)
            
            self.PLShutter.write(bytes(b"ens?\r"))
            ans = self.PLShutter.read(size = 100)
            if b'0' in ans:
                self.PLShutter.write(bytes(b"ens\r"))
                self.PLShutter.read(size = 100)
                time.sleep(1)
                
            ans = self.PLShutter.read(size = 100)
            if b'0' in ans:
                print('Error: Cannot Open PL Shutter')
                sys.exit(app.exec_())
            
            
            #Begin the PL Measurement after Cooling
            
            CooledfullRunPath = os.path.join(self.directoryPath, runString, 'Cooled')
            if not os.path.exists(CooledfullRunPath):
                os.mkdir(CooledfullRunPath)
            
            self.typeLabel.setText('PL Cooling Time Remaining (min): ')
            self.typeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
            QApplication.processEvents()
            
            time_graph = []
            count_graph = []
            allCounts = []
            areaCurve = []
            normalizedCounts = []
            maxIntensities = []
            spectrum_array = []
            
            #Step 11: Begin the Cooling PL Measurements    
            for z in range(self.PLTime.value()*60,0,-1):
                self.minutesRemaining.display(z/60)
                #Get the laser spectrum
                pmt.write(bytes(B'S\r'))
                wavelength = sb.getWavelength()
                rawIntensity = sb.getIntensity()
                intensity = rawIntensity - backgroundIntensity
                
                #Get the PMT Counts
                
                try:
                    sol = pmt.read(400) #this reads the 4 bytes of data
                    time.sleep(0.01)
                    counts = sol[0]*16777216+sol[1]*65536+sol[2]*256+sol[3]
                except IndexError:
                    counts = 0
                    pass                
                
                
                #Correcting the Data                
                PLWavelength = wavelength[(wavelength>=508) & (wavelength <= 522)]
                PLIntensity = intensity[(wavelength>=508) & (wavelength <= 522)]
                
                #Getting the background
                PLBackground = np.mean(intensity[(wavelength>=430) & (wavelength <= 480)])
                #Normalized Intenisty
                
                PLIntenistyBackgroundCorrected = PLIntensity-PLBackground
                #Area Under the Curve (total light emitted)
                areaUnderCurve = np.trapz(PLIntenistyBackgroundCorrected, x = PLWavelength)
                
                maxIntensity = np.max(PLIntenistyBackgroundCorrected)
                normalized_Counts = counts/areaUnderCurve*1000
                
                
                elapsedTime = time.time()-startTime
                #time_graph.append(elapsedTime)
                #count_graph.append(counts)
                
                #Saving the data
                runStr = 'CooledSpectrumAndCounts'+str(z)+'ofRun' + str(x) + '.h5'
                name = os.path.join(CooledfullRunPath, runStr)
                f = h5py.File(name, "w")
                f.create_dataset(name, data=True)
                f.create_dataset('Time', data = elapsedTime)
                f.create_dataset('Spectrum', data = y)
                f.create_dataset('Wavelength', data = wavelength)
                f.create_dataset('Intensity', data = intensity)
                f.create_dataset('Analyzed Wavelength', data = PLWavelength)
                f.create_dataset('Background Corrected Intensity', data = PLIntenistyBackgroundCorrected)
                f.create_dataset('Counts', data = counts)
                f.create_dataset('Area Under Curve', data = areaUnderCurve)
                f.create_dataset('Normalized Counts', data = normalized_Counts)
                f.create_dataset('Max Intensity', data = maxIntensity)
                f.close()
                
                #Saving the Data
                spectrum_array.append(y)
                time_graph.append(elapsedTime)
                count_graph.append(counts)
                areaCurve.append(areaUnderCurve)
                maxIntensities.append(maxIntensity)
                normalizedCounts.append(normalized_Counts)
                
                #Plot the Data
                self.luminescencePlot = self.PLPlot.plot(wavelength, intensity, clear = True, pen = pg.mkPen('r'))
                self.luminescencePlot.setPen((0,0,0))
                font = QFont('Times New Roman', 12)
                labelStyle = {'color': 'k', 'font-size': '10pt'}
                self.PLPlot.setLabel('bottom', text = 'Wavelength (nm)', **labelStyle)
                self.PLPlot.setLabel('left', text = 'Intensity (a.u.)',**labelStyle)
                self.PLPlot.setLabel('top', 'Laser Spectrum',**labelStyle)
                
                #Plot the Counts
        
                self.normalizedCountsPlot = self.countsPlot.plot(time_graph, count_graph)
                self.normalizedCountsPlot.setPen((0,0,0))
                font = QFont('Times New Roman', 12)
                labelStyle = {'color': 'k', 'font-size': '10pt'}
                self.countsPlot.setLabel('bottom', text = 'Elapsed Time (s)',**labelStyle)
                self.countsPlot.setLabel('left', text = 'Counts', **labelStyle)
                self.countsPlot.setLabel('top', 'PMT Counts')
                
                #Counts Plot 
                QApplication.processEvents()
                
                timeRemaining = 0.95-(time.time()-startTime)
                if timeRemaining > 0:
                    time.sleep(timeRemaining)


            CooledRunDataname = os.path.join(CooledfullRunPath, 'Cooled Run ' +  str(x) + ' Data.h5')
            f2 = h5py.File(CooledRunDataname, "w")
            f2.create_dataset(CooledRunDataname, data=True)
            f2.create_dataset('Elasped Time', data = time_graph)
            f2.create_dataset('Spectrum', data = spectrum_array)
            f2.create_dataset('Counts', data = count_graph)
            f2.create_dataset('Area Under Curve', data = areaCurve)
            f2.create_dataset('Max Intensity', data = maxIntensities)
            f2.create_dataset('Normalized Counts', data = normalizedCounts)
            f2.close()
                
            #Step 12: Close the PL shutter
            self.PLShutter.write(bytes(b"\r"))
            self.PLShutter.read(size = 100)
            
            self.PLShutter.write(bytes(b"ens?\r"))
            ans = self.PLShutter.read(size = 100)
            if b'1' in ans:
                self.PLShutter.write(bytes(b"ens\r"))
                self.PLShutter.read(size = 100)
                time.sleep(1)
                
            ans = self.PLShutter.read(size = 100)
            if b'1' in ans:
                print('Error: Cannot Open Cooling Shutter')
                sys.exit(app.exec_())
                
            #Step 13: Analyze the data
            
            #Analysis path
            saveRunPath = os.path.join(self.directoryPath, runString, 'Analysis')
            if not os.path.exists(saveRunPath):
                os.mkdir(saveRunPath)
            
            #Room temperature file
            rt = h5py.File(RunDataname, 'r')
            
            #Get the data from the file
            RTspectrum = np.array(rt.get('Spectrum'))
            RTelapsedTime = np.array(rt.get('Elasped Time'))
            RTcounts = np.array(rt.get('Counts'))
            RTareaUnderCurve = np.array(rt.get('Area Under Curve'))
            RTspectrumNormal = RTspectrum[::-1]
            
            #Replace the zeros and pegged values with the mean

            #remove the spikes

            RTcounts[RTcounts>10000] = 0

            #Remove the zeroes
            avg = np.mean(RTcounts[RTcounts>0])

            RTcounts[RTcounts==0] = avg

            #Close the file
            rt.close()
            
            #Opening Cooling Files
            cf = h5py.File(CooledRunDataname, 'r')
            #Get the data from the file
            cooledSpectrum = np.array(cf.get('Spectrum'))
            cooledElapsedTime = np.array(cf.get('Elasped Time'))
            cooledCounts = np.array(cf.get('Counts'))
            cooledAreaUnderCurve = np.array(cf.get('Area Under Curve'))
            cooledSpectrumNormal = cooledSpectrum[::-1]

            #Replace the zeros and pegged values with the mean

            #remove the spikes

            cooledCounts[cooledCounts>10000] = 0

            #Remove the zeroes
            avg = np.mean(cooledCounts[cooledCounts>0])

            cooledCounts[cooledCounts==0] = avg


            #Close the file
            cf.close()
            
            #Normalize the data
            RTnormArea = RTareaUnderCurve/RTareaUnderCurve[-1]
            cooledNormArea = cooledAreaUnderCurve/RTareaUnderCurve[-1]

            RTnormalizedCounts = np.divide(RTcounts,RTnormArea)
            cooledNormalizedCounts = np.divide(cooledCounts,cooledNormArea)
            
            #Determine if Cooling is occuring
            oneSpectrum = cooledNormalizedCounts[0] > RTnormalizedCounts[-1]
            oneSpectrumCooled = (cooledNormalizedCounts[0] - RTnormalizedCounts[-1])/RTnormalizedCounts[-1]*100
            twoSpectra = np.mean(cooledNormalizedCounts[0:1]) > np.mean(RTnormalizedCounts[-2:])
            twoSpectraCooled = (np.mean(cooledNormalizedCounts[0:1])-np.mean(RTnormalizedCounts[-2:]))/np.mean(RTnormalizedCounts[-2:])*100
            threeSpectra = np.mean(cooledNormalizedCounts[0:2]) > np.mean(RTnormalizedCounts[-3:])
            threeSpectraCooled = (np.mean(cooledNormalizedCounts[0:2])-np.mean(RTnormalizedCounts[-3:]))/np.mean(RTnormalizedCounts[-3:])*100

 

            #Writing the files to show cooling
            if oneSpectrum:
                pth = os.path.join(saveRunPath,'Cooled_OneAverageNormalized.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts :' + str(cooledNormalizedCounts[0]) + '\n')
                f.write('RT Normalized Counts :' + str(RTnormalizedCounts[-1]) + '\n')
                f.write('Cooled Percentage (%):' + str(oneSpectrumCooled)+ '\n')
                f.close()
            else:
                pth = os.path.join(saveRunPath,'Heated_OneAverageNormalized.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts :' + str(cooledNormalizedCounts[0]) + '\n')
                f.write('RT Normalized Counts :' + str(RTnormalizedCounts[-1]) + '\n')
                f.write('Cooled Percentage (%):' + str(oneSpectrumCooled)+ '\n')
                f.close()
    

            if twoSpectra:
                pth = os.path.join(saveRunPath,'Cooled_TwoAverageNormalized.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledNormalizedCounts[0:1])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledNormalizedCounts[0:1])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTnormalizedCounts[-2:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTnormalizedCounts[-2:])) + '\n')
                f.write('Cooled Percentage (%):' + str(twoSpectraCooled)+ '\n')
                f.close()
            else:
                pth = os.path.join(saveRunPath,'Heated_TwoAverageNormalized.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledNormalizedCounts[0:1])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledNormalizedCounts[0:1])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTnormalizedCounts[-2:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTnormalizedCounts[-2:])) + '\n')
                f.write('Cooled Percentage (%):' + str(twoSpectraCooled)+ '\n')
                f.close()


            if threeSpectra:
                pth = os.path.join(saveRunPath,'Cooled_ThreeAverageNormalized.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledNormalizedCounts[0:2])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledNormalizedCounts[0:2])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTnormalizedCounts[-3:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTnormalizedCounts[-3:])) + '\n')
                f.write('Cooled Percentage (%):' + str(threeSpectraCooled)+ '\n')
                f.close()
            else:
                pth = os.path.join(saveRunPath,'Heated_ThreeAverageNormalized.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledNormalizedCounts[0:2])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledNormalizedCounts[0:2])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTnormalizedCounts[-3:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTnormalizedCounts[-3:])) + '\n')
                f.write('Cooled Percentage (%):' + str(threeSpectraCooled)+ '\n')
                f.close()

            #Determine if cooling is occuring for non normlized data

            SpectrumOne = cooledCounts[0] > RTcounts[-1]
            SpectrumCooledOne = (cooledCounts[0] - RTcounts[-1])/RTcounts[-1]*100
            SpectraTwo = np.mean(cooledCounts[0:1]) > np.mean(RTcounts[-2:])
            SpectraCooledTwo = (np.mean(cooledCounts[0:1])-np.mean(RTcounts[-2:]))/np.mean(RTcounts[-2:])*100
            SpectraThree = np.mean(cooledCounts[0:2]) > np.mean(RTcounts[-3:])
            SpectraCooledThree = (np.mean(cooledCounts[0:2])-np.mean(RTcounts[-3:]))/np.mean(RTcounts[-3:])*100

            if SpectrumOne:
                pth = os.path.join(saveRunPath,'Cooled_OneAverage.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts :' + str(cooledCounts[0]) + '\n')
                f.write('RT Normalized Counts :' + str(RTcounts[-1]) + '\n')
                f.write('Cooled Percentage (%):' + str(SpectrumCooledOne)+ '\n')
                f.close()
            else:
                pth = os.path.join(saveRunPath,'Heated_OneAverage.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts :' + str(cooledCounts[0]) + '\n')
                f.write('RT Normalized Counts :' + str(RTcounts[-1]) + '\n')
                f.write('Cooled Percentage (%):' + str(SpectrumCooledOne)+ '\n')
                f.close()


            if SpectraTwo:
                pth = os.path.join(saveRunPath,'Cooled_TwoAverage.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledCounts[0:1])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledCounts[0:1])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTcounts[-2:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTcounts[-2:])) + '\n')
                f.write('Cooled Percentage (%):' + str(SpectraCooledTwo)+ '\n')
                f.close()
            else:
                pth = os.path.join(saveRunPath,'Heated_TwoAverage.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledCounts[0:1])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledCounts[0:1])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTcounts[-2:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTcounts[-2:])) + '\n')
                f.write('Cooled Percentage (%):' + str(SpectraCooledTwo)+ '\n')
                f.close()
    
            if SpectraThree:
                pth = os.path.join(saveRunPath,'Cooled_ThreeAverage.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledCounts[0:2])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledCounts[0:2])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTcounts[-3:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTcounts[-3:])) + '\n')
                f.write('Cooled Percentage (%):' + str(SpectraCooledThree)+ '\n')
                f.close()
            else:
                pth = os.path.join(saveRunPath,'Heated_ThreeAverage.txt')
                f = open(pth, 'w')
                f.write('Cooled Normalized Counts Avg :' + str(np.mean(cooledCounts[0:2])) + '\n')
                f.write('Cooled Normalized Counts Std :' + str(np.std(cooledCounts[0:2])) + '\n')
                f.write('RT Normalized Counts Avg:' + str(np.mean(RTcounts[-3:])) + '\n')
                f.write('RT Normalized Counts Std:' + str(np.std(RTcounts[-3:])) + '\n')
                f.write('Cooled Percentage (%):' + str(SpectraCooledThree)+ '\n')
                f.close()

            
            #Step 14: Sample equilibrium time
            
            self.typeLabel.setText('Sample Equilibrium Time Remaining (min): ')
            self.typeLabel.setStyleSheet("QLabel {font: bold Large; font-family: 'Times New Roman'; font-size: 20px; color: red}")
            QApplication.processEvents()
            
            for b in range(self.eqTime.value()*60,0,-1):
                self.minutesRemaining.display(b/60)
                time.sleep(1)
                QApplication.processEvents()






#This creates the actual window when Python runs and keeps it running until 
# you close the window
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())