"use client";

import Image from "next/image";
import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';

//default input values
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

 // Register Chart.js components
 Chart.register(...registerables);

// Temperature chart component
function TemperatureChart({dateFrom, dateTo}) {
    const [chartData, setChartData] = useState({
        labels: [],
        datasets: [
            {
                label: 'Bit Error Rate',
                data: [],
                fill: false,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                tension: 0.1
            },
            {
                label: 'Temperature',
                data: [],
                fill: false,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                tension: 0.1
            }
        ]
    });
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        
        // Fetch bit error rate data
        const berPromise = fetch(`/api/get-chart?metric=bitErrorRate&dateFrom=${dateFrom}&dateTo=${dateTo}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch BER data');
                return response.json();
            });
        
        // Fetch temperature data
        const tempPromise = fetch(`/api/get-chart?metric=temperature&dateFrom=${dateFrom}&dateTo=${dateTo}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch temperature data');
                return response.json();
            });

        // Wait for both requests to complete
        Promise.all([berPromise, tempPromise])
            .then(([berData, tempData]) => {
                setChartData({
                    labels: berData.x, // both datasets have the same x values
                    datasets: [
                        {
                            ...chartData.datasets[0],
                            data: berData.y
                        },
                        {
                            ...chartData.datasets[1],
                            data: tempData.y
                        }
                    ]
                });
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching chart data:', err);
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading chart data...</div>;
    if (error) return <div>Error loading chart data: {error}</div>;

    const options = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Values'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                }
            }
        }
    };

    return <Line data={chartData} options={options} />;
};

//Humidity chart component
function HumidityChart({dateFrom, dateTo}) {
    const [chartData, setChartData] = useState({
        labels: [],
        datasets: [
            {
                label: 'Bit Error Rate',
                data: [],
                fill: false,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                tension: 0.1,
                yAxisID: 'y-ber'
            },
            {
                label: 'Humidity',
                data: [],
                fill: false,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                tension: 0.1,
                yAxisID: 'y-humidity'
            }
        ]
    });
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch bit error rate data
        const berPromise = fetch(`/api/get-chart?metric=bitErrorRate&dateFrom=${dateFrom}&dateTo=${dateTo}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch BER data');
                return response.json();
            });
        
        // Fetch humidity data
        const humidityPromise = fetch(`/api/get-chart?metric=relativeHumidity&dateFrom=${dateFrom}&dateTo=${dateTo}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch humidity data');
                return response.json();
            });

        // Wait for both requests to complete
        Promise.all([berPromise, humidityPromise])
            .then(([berData, humidityData]) => {
                
                setChartData({
                    labels: berData.x, // both datasets have the same x values
                    datasets: [
                        {
                            ...chartData.datasets[0],
                            data: berData.y
                            //originalData: berData.y // store original values for tooltips
                        },
                        {
                            ...chartData.datasets[1],
                            data: humidityData.y
                        }
                    ]
                });
                setLoading(false);
            })
            .catch(err => {
                console.error('Error fetching chart data:', err);
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading chart data...</div>;
    if (error) return <div>Error loading chart data: {error}</div>;

    const options = {
        responsive: true,
        scales: {
            'y-humidity': {
                type: 'linear' as const,
                position: 'left' as const,
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Humidity (%)'
                },
                grid: {
                    drawOnChartArea: true
                }
            },
            'y-ber': {
                type: 'linear' as const,
                position: 'right' as const,
                min: 0,
                title: {
                    display: true,
                    text: 'Bit Error Rate (normalized)'
                },
                grid: {
                    drawOnChartArea: false
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                }
            }
        }
    };
    return <Line data={chartData} options={options} />;
};


export default function Home() {
  useInitialization(); // document.ready replacement
  const defaultDateFrom = "2025-04-07";
  const defaultDateTo = "2025-04-10";

  const [dateFrom, setDateFrom] = useState(defaultDateFrom);
  const [dateTo, setDateTo] = useState(defaultDateTo);
  const [dateRender, setDateRender] = useState(true);

  function handleDateChange(event){
    if(event.target.id == 'from'){
        setDateFrom(event.target.value);
    }else{
        setDateTo(event.target.value);
    }
    setDateRender(false)
    setTimeout(() => setDateRender(true), 1);
  }
  

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
                                    console.log("Change Location button clicked!");
                                }}
                            >
                                Change Location
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
                    <input type="date" id="from" className="dateInput" value={dateFrom} onChange={handleDateChange}></input> to <input type="date" id="to" className="dateInput"value={dateTo} onChange={handleDateChange}></input>
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
                    <div className="chart-container" style={{ height: '400px' }}>
                        {dateRender && <TemperatureChart dateFrom={dateFrom} dateTo={dateTo}/>}
                    </div>
                </div>
                {/* Humidity */}
                <div id="humidChart">
                    <h2>Humidity</h2>
                    <hr />
                    <div className="chart-container" style={{ height: '400px' }}>
                        {dateRender && <HumidityChart dateFrom={dateFrom} dateTo={dateTo}/>}
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
}
