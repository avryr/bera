"use client";

import Image from "next/image";
import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { useEffect } from 'react';

//default locations for top bar
const defaultLoc1 = 'W8EDU';
const defaultLoc2 = 'NA8SA';
//funcs
function changeLocs(loc1 : string, loc2 : string) {
    // Set the text of the location spans
    $('#loc1').text(loc1);
    $('#loc2').text(loc2);
}
function toggleChart(divID : string) {
    $(divID).toggle();
    console.log(divID + " clicked!");
}

// React useEffect hook instead of jQuery document ready
function useInitialization() {
  useEffect(() => {
    changeLocs(defaultLoc1, defaultLoc2);
    // Set checkboxes to unchecked
    $('input[type=checkbox]').prop('checked', false);
  }, []); // Empty dependency array means this runs once on mount... I hope
}

export default function Home() {
  useInitialization(); // document.ready replacement

  return (
    <div className="container-fluid">
        {/* Header */}
        <div className="row">
            {/* Logo */}
            <div className="col-sm-2 pageTitle d-flex justify-content-center align-items-center">
                <img src="/bera.svg" className="logo" alt="BERA Logo" />
            </div>
            {/* Location Display */}
            <div className="col-sm-10">
                <div className="row header">
                    <div className="col-sm-9 d-flex justify-content-center align-items-center" style={{ minHeight: "100%" }}>
                        <div className="panel panel-body locationDisplay">
                            <span id="loc1"></span> <i className="arrow fa-solid fa-arrow-right"></i> <span id="loc2"></span>
                        </div>
                    </div>
                    <div className="col-sm-1"></div>
                    {/* Change Location Button */}
                    <div className="col-sm-2">
                        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "100%" }}>
                            <button 
                                type="button" 
                                className="btn locationBtn"
                                onClick={() => {
                                    fetch('/api/get-cheese')
                                        .then(response => response.text())
                                        .then(data => {
                                            $('.locationBtn').text(data);
                                        })
                                        .catch(error => {
                                            console.error('Error fetching cheese data:', error);
                                            $('.locationBtn').text('Error loading');
                                        });
                                }}
                            >
                                Get Cheese
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {/* Document */}
        <div className="row">
            {/* Sidebar */}
            <div className="col-sm-2 sidebar">
                <h1>Data</h1>
                <hr />
                {/* Checklist */}
                <div className="checks">
                    <div className="form-check">
                        <input 
                          className="form-check-input" 
                          type="checkbox" 
                          id="precip" 
                          onChange={() => toggleChart('#precipChart')}
                        />
                        <label className="form-check-label" htmlFor="precip">
                            Precipitation
                        </label>
                    </div>
                    <p></p>
                    <div className="form-check">
                        <input 
                          className="form-check-input" 
                          type="checkbox" 
                          id="temp"
                          onChange={() => toggleChart('#tempChart')}
                        />
                        <label className="form-check-label" htmlFor="temp">
                            Temperature
                        </label>
                    </div>
                    <p></p>
                    <div className="form-check">
                        <input 
                          className="form-check-input" 
                          type="checkbox" 
                          id="humid"
                          onChange={() => toggleChart('#humidChart')}
                        />
                        <label className="form-check-label" htmlFor="humid">
                            Humidity
                        </label>
                    </div>
                </div>
            </div>
            {/* Sidebar Footer */}
            <div className="col-sm-2 setToBottom">
                <div className ="dates">
                    <h4>From</h4>
                    <input type="date" className="dateInput"></input> to <input type="date" className="dateInput"></input>
                </div>
                <hr />
                <div className="sideLink">
                    <a href="https://github.com/avryr/bera">Link to our GitHub...</a>
                </div>
            </div>
            {/* Charts */}
            <div className="col-sm-10 charts">
                {/* Precipitation */}
                <div id="precipChart">
                    <h2>Precipitation</h2>
                    <hr />
                </div>
                {/* Temperature */}
                <div id="tempChart">
                    <h2>Temperature</h2>
                    <hr />
                </div>
                {/* Humidity */}
                <div id="humidChart">
                    <h2>Humidity</h2>
                    <hr />
                </div>
            </div>
        </div>
    </div>
  );
}
