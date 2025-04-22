"use client";

import $ from 'jquery';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';

// CHART COLOR VARIABLES (in Hex)
//  * "ber" -- Bit Error Rate line colors
const berBackground = '#E56B6F';
const berOutline = '#D593B7';
//  * "weath" -- Weather component (temperature, pressure, etc.) metric line colors
const weathBackground = '#4E445F';
const weathOutline = '#67597A';

// React useEffect hook
function useInitialization() {
    useEffect(() => {
        //Ensures checkboxes are not checked on reload.
        $('input[type=checkbox]').prop('checked', false);
    }, []); // Empty dependency array means this runs once on mount
}

// Register Chart.js components
Chart.register(...registerables);

// Generic chart component that handles all weather metrics
function MetricChart({ 
    dateFrom, 
    dateTo, 
    metric,
    station,
    title, 
    unit, 
    minValue = undefined, 
    maxValue = undefined 
}: { 
    dateFrom: string, 
    dateTo: string, 
    metric: string,
    station?: string, 
    title: string, 
    unit: string,
    minValue?: number,
    maxValue?: number 
}) {
    const [chartData, setChartData] = useState({
        labels: [],
        datasets: [
            {
                label: 'Bit Error Rate',
                data: [],
                fill: false,
                backgroundColor: berBackground,
                borderColor: berOutline,
                borderWidth: 1,
                tension: 0.1,
                yAxisID: 'y-ber'
            },
            {
                label: title,
                data: [],
                fill: false,
                backgroundColor: weathBackground,
                borderColor: weathOutline,
                borderWidth: 1,
                tension: 0.1,
                yAxisID: 'y-metric'
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

        // Fetch metric data
        const metricPromise = fetch(`/api/get-chart?metric=${metric}&dateFrom=${dateFrom}&dateTo=${dateTo}&station=${station}`)
            .then(response => {
                if (!response.ok) throw new Error(`Failed to fetch ${metric} data`);
                return response.json();
            });

        // Wait for both requests to complete
        Promise.all([berPromise, metricPromise])
            .then(([berData, metricData]) => {
                // Format timestamps into "month/day hour:minute"
                const formattedLabels = berData.x.map((timestamp: string) => {
                    const date = new Date(timestamp);
                    return date.toLocaleString('en-US', {
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false // Use 24-hour format; remove if you want 12-hour format
                    });
                });

                // Special handling for pressure (convert Pa to hPa)
                const metricValues = metric === 'barometricPressure' 
                    ? metricData.y.map((value: number) => value / 100)
                    : metricData.y;

                setChartData({
                    labels: formattedLabels,
                    datasets: [
                        {
                            ...chartData.datasets[0],
                            data: berData.y
                        },
                        {
                            ...chartData.datasets[1],
                            data: metricValues
                        }
                    ]
                });
                setLoading(false);
            })
            .catch(err => {
                console.error(`Error fetching ${metric} chart data:`, err);
                setError(err.message);
                setLoading(false);
            });
    }, [dateFrom, dateTo, metric]);

    if (loading) return <div>Loading chart data...</div>;
    if (error) return <div>Error loading chart data: {error}</div>;

    const options = {
        responsive: true,
        scales: {
            'y-metric': {
                type: 'linear' as const,
                position: 'left' as const,
                beginAtZero: minValue === undefined,
                min: minValue,
                max: maxValue,
                title: {
                    display: true,
                    text: `${title} (${unit})`
                },
                grid: {
                    drawOnChartArea: true
                }
            },
            'y-ber': {
                type: 'linear' as const,
                position: 'right' as const,
                min: 0,
                max: 1,
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
}

// Functions to generate specific charts:
//  * Takes dateFrom, dateTo, and station as paramets to draw the chart
//  * NOTE: Charts must be reloaded using the reload function in order to redraw when a state is changed.
function TemperatureChart({ dateFrom, dateTo, station  }: { dateFrom: string, dateTo: string, station: string}) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="temperature"
        station={station} 
        title="Temperature" 
        unit="°C" 
    />;
}

function HumidityChart({ dateFrom, dateTo, station}: { dateFrom: string, dateTo: string, station: string}) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="relativeHumidity"
        station={station}
        title="Humidity" 
        unit="%" 
    />;
}

function DewpointChart({ dateFrom, dateTo, station }: { dateFrom: string, dateTo: string, station: string}) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="dewpoint"
        station={station} 
        title="Dew point" 
        unit="°C" 
    />;
}

function PrecipitationChart({ dateFrom, dateTo, station }: { dateFrom: string, dateTo: string, station: string}) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="precipitation"
        station={station} 
        title="Precipitation" 
        unit="cm" 
    />;
}

function PressureChart({ dateFrom, dateTo, station }: { dateFrom: string, dateTo: string, station: string}) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="barometricPressure"
        station={station} 
        title="Barometric pressure" 
        unit="hPa" 
        minValue={700}
        maxValue={1500}
    />;
}

export default function Home() {
    useInitialization(); // document.ready replacement

    // Calculates and sets default date values for date input.
    //  * Defaulted to display data from the last 7 days.
    const DateFrom = new Date();
    DateFrom.setDate(DateFrom.getDate() - 7);
    const DateTo = new Date();
    DateTo.setDate(DateTo.getDate() + 1);
    const defaultDateFrom = DateFrom.toISOString().split('T')[0];
    const defaultDateTo = DateTo.toISOString().split('T')[0];

    const [dateFrom, setDateFrom] = useState(defaultDateFrom); //State for "from" date input.
    const [dateTo, setDateTo] = useState(defaultDateTo); //State for "to" date input. 
    const [dateRender, setDateRender] = useState(true); //State for rendering charts. Useful for reloading.
    const [station, setStation] = useState('CWRU'); //State for weather station.

    //Function to reload charts. Sets renderer to false then back to true.
    function reloadCharts() {
        setDateRender(false)
        setTimeout(() => setDateRender(true), 0);
    }

    //Function for handling a date change from both date inputs. Reloads charts.
    function handleDateChange(event: React.ChangeEvent<HTMLInputElement>) {
        if (event.target.id == 'from') {
            setDateFrom(event.target.value);
        } else {
            setDateTo(event.target.value);
        }
        reloadCharts();
    }

    //Function for handling a weather station change from dropdown menu. Reloads Charts
    function handleStationChange(event: React.ChangeEvent<HTMLSelectElement>){
        setStation(event.target.value);
        reloadCharts();
    }

    //Function to handle a chart's visibility toggle, called by checklist checks' onChange
    function toggleChart(divID: string) {
        $(divID).toggle();
    }

    //Returns HTML for the webpage.
    return (
        <div className="container-fluid">
            {/* Header */}
            <div className="row topBar">
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
                                <select className="custom-select locationBtn" onChange={handleStationChange}>
                                    <option defaultValue='true' value="CWRU">CWRU</option>
                                    <option value={"KCLE"}>KCLE</option>
                                    <option value="KBKL">KBKL</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {/* Document */}
            <div className="row inner">
                {/* Sidebar */}
                <div className="col-sm-2 sidebar">
                    <h1>Data</h1>
                    <hr />
                    {/* Checklist */}
                    <div className="checks">
                        {/* Precipitation Check */}
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
                        {/* Temperature Check */}
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
                        {/* Humidity Check */}
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
                        <p></p>
                        {/* Dewpoint Check */}
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="dew"
                                onChange={() => toggleChart('#dewChart')}
                            />
                            <label className="form-check-label" htmlFor="dew">
                                Dewpoint
                            </label>
                        </div>
                        <p></p>
                        {/* Pressure Check */}
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="pressure"
                                onChange={() => toggleChart('#pressureChart')}
                            />
                            <label className="form-check-label" htmlFor="pressure">
                                Pressure
                            </label>
                        </div>
                    </div>
                </div>
                {/* Sidebar Footer */}
                <div className="col-sm-2 setToBottom">
                    <div className="dates">
                        <h4>From</h4>
                        <input type="date" id="from" className="dateInput" value={dateFrom} onChange={handleDateChange}></input> to <input type="date" id="to" className="dateInput" value={dateTo} onChange={handleDateChange}></input>
                    </div>
                    <hr />
                    <div className="sideLink">
                        <a href="https://github.com/avryr/bera">Link to our GitHub...</a>
                    </div>
                </div>
                {/* Charts */}
                <div className = "col-sm-2"></div>
                <div className="col-sm-10 charts">
                    {/* Precipitation Chart */}
                    <div id="precipChart">
                        <h2>Precipitation</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <PrecipitationChart dateFrom={dateFrom} dateTo={dateTo} station={station}/>}
                        </div>
                    </div>
                    {/* Temperature Chart */}
                    <div id="tempChart">
                        <h2>Temperature</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <TemperatureChart dateFrom={dateFrom} dateTo={dateTo} station={station}/>}
                        </div>
                    </div>
                    {/* Humidity Chart */}
                    <div id="humidChart">
                        <h2>Humidity</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <HumidityChart dateFrom={dateFrom} dateTo={dateTo} station={station}/>}
                        </div>
                    </div>
                    {/* Dewpoint Chart */}
                    <div id="dewChart">
                        <h2>Dewpoint</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <DewpointChart dateFrom={dateFrom} dateTo={dateTo} station={station}/>}
                        </div>
                    </div>
                    {/* Pressure Chart */}
                    <div id="pressureChart">
                        <h2>Pressure</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <PressureChart dateFrom={dateFrom} dateTo={dateTo} station={station}/>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
