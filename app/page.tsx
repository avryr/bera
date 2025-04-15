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
const defaultLoc2 = 'N8OBJ';

//chart colors
const berBackground = '#E56B6F';
const berOutline = '#D593B7';
const weathBackground = '#4E445F';
const weathOutline = '#67597A';

//funcs
function changeLocs(loc1: string, loc2: string) {
    // Set the text of the location spans
    $('#loc1').text(loc1);
    $('#loc2').text(loc2);
}
function toggleChart(divID: string) {
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

// Generic chart component that handles all weather metrics
function MetricChart({ 
    dateFrom, 
    dateTo, 
    metric,
    station = "CWRU", 
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
                // Special handling for pressure (convert Pa to hPa)
                const metricValues = metric === 'barometricPressure' 
                    ? metricData.y.map((value: number) => value / 100)
                    : metricData.y;

                setChartData({
                    labels: berData.x,
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

// Specific chart components that use the generic component
function TemperatureChart({ dateFrom, dateTo }: { dateFrom: string, dateTo: string }) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="temperature" 
        title="Temperature" 
        unit="°C" 
    />;
}

function HumidityChart({ dateFrom, dateTo }: { dateFrom: string, dateTo: string }) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="relativeHumidity" 
        title="Humidity" 
        unit="%" 
    />;
}

function DewpointChart({ dateFrom, dateTo }: { dateFrom: string, dateTo: string }) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="dewpoint" 
        title="Dew point" 
        unit="°C" 
    />;
}

function PrecipitationChart({ dateFrom, dateTo }: { dateFrom: string, dateTo: string }) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="precipitation" 
        title="Precipitation" 
        unit="cm" 
    />;
}

function PressureChart({ dateFrom, dateTo }: { dateFrom: string, dateTo: string }) {
    return <MetricChart 
        dateFrom={dateFrom} 
        dateTo={dateTo} 
        metric="barometricPressure" 
        title="Barometric pressure" 
        unit="hPa" 
        minValue={700}
        maxValue={1500}
    />;
}

export default function Home() {
    useInitialization(); // document.ready replacement
    // default date range: 7 days from today
    const DateFrom = new Date();
    DateFrom.setDate(DateFrom.getDate() - 7);
    const DateTo = new Date();
    DateTo.setDate(DateTo.getDate() + 1);
    const defaultDateFrom = DateFrom.toISOString().split('T')[0];
    const defaultDateTo = DateTo.toISOString().split('T')[0];

    const [dateFrom, setDateFrom] = useState(defaultDateFrom);
    const [dateTo, setDateTo] = useState(defaultDateTo);
    const [dateRender, setDateRender] = useState(true);

    function reloadCharts() {
        setDateRender(false)
        setTimeout(() => setDateRender(true), 1);
    }


    function handleDateChange(event: React.ChangeEvent<HTMLInputElement>) {
        if (event.target.id == 'from') {
            setDateFrom(event.target.value);
        } else {
            setDateTo(event.target.value);
        }
        reloadCharts();
    }


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
            <div className="row inner">
                {/* Sidebar */}
                <div className="col-sm-2 sidebar">
                    <h1>Data</h1>
                    <hr />
                    {/* Checklist */}
                    <div className="checks">
                        {/* Precipitation */}
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
                        {/* Temperature */}
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
                        {/* Humidity */}
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
                        {/* Dewpoint */}
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
                        {/* Pressure */}
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
                    {/* Precipitation */}
                    <div id="precipChart">
                        <h2>Precipitation</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <PrecipitationChart dateFrom={dateFrom} dateTo={dateTo} />}
                        </div>
                    </div>
                    {/* Temperature */}
                    <div id="tempChart">
                        <h2>Temperature</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <TemperatureChart dateFrom={dateFrom} dateTo={dateTo} />}
                        </div>
                    </div>
                    {/* Humidity */}
                    <div id="humidChart">
                        <h2>Humidity</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <HumidityChart dateFrom={dateFrom} dateTo={dateTo} />}
                        </div>
                    </div>
                    {/* Dewpoint */}
                    <div id="dewChart">
                        <h2>Dewpoint</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <DewpointChart dateFrom={dateFrom} dateTo={dateTo} />}
                        </div>
                    </div>
                    {/* Pressure */}
                    <div id="pressureChart">
                        <h2>Pressure</h2>
                        <hr />
                        <div className="chart-container" style={{ height: '400px' }}>
                            {dateRender && <PressureChart dateFrom={dateFrom} dateTo={dateTo} />}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
