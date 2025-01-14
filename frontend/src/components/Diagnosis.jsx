import React, { useState } from 'react';
import { Modal } from 'react-bootstrap';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip } from 'chart.js';
import 'bootstrap/dist/css/bootstrap.min.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip);

const Diagnosis = ({ data }) => {

    const emptyData = {
        'name': "",
        'precautions': [],
        'link': "",
        'drugs': [],
        'drug_links': []
    };

    const { labels, points } = data;
    const [diseaseData, setDiseaseData] = useState(emptyData);
    const [showModal, setShowModal] = useState(false);

    const datasets = labels.map((label, index) => ({
        label: label,
        data: [points[index]],
        backgroundColor: 'rgba(134, 31, 194, 0.7)',
        borderColor: 'rgba(134, 31, 194, 1)',
        borderWidth: 1
    }));

    const chartData = {
        labels: ['Disease'],
        datasets: datasets 
    }

    const fetchDiseaseData = async (disease) => {
        const url = `http://localhost:5000/disease?name=${encodeURIComponent(disease)}`;
        const response = await fetch(url);
        const result = await response.json();

        let newDiseaseData = {};
        newDiseaseData["name"] = result.name;
        newDiseaseData["precautions"] = result.precautions;
        newDiseaseData["link"] = result.link;
        newDiseaseData["drugs"] = result.drugs;
        newDiseaseData["drug_links"] = result.drug_links;

        console.log(newDiseaseData);
        setDiseaseData(newDiseaseData);
        setShowModal(true);
    }

    const options = {
        indexAxis: 'y',
        responsive: true,
        scales: {
            x: {
                beginAtZero: true
            },
            y: {
                beginAtZero: true
            }
        },
        onClick: async (e) => {
            const chart = e.chart;
            const bar = chart.getElementsAtEventForMode(e.native, 'nearest', { intersect: true }, false);
            if (bar.length) {
                const index = bar[0].datasetIndex;
                const disease = datasets[index].label;
                await fetchDiseaseData(disease);
            }
        }
    };

    return (
        <div className='chart'>
            <Bar data={chartData} options={options} />   
            <Modal show={showModal} onHide={() => setShowModal(false)} className='disease-modal' backdrop="static">
                <Modal.Header closeButton>
                    {diseaseData.link !== "" && (
                        <a href={diseaseData.link} target='_blank'>
                        <Modal.Title>
                            {diseaseData.name}
                        </Modal.Title>
                        </a>
                    )}
                    {diseaseData.link === "" && <Modal.Title> {diseaseData.name} </Modal.Title>}
                </Modal.Header>
                <Modal.Body>
                    {diseaseData.precautions.length > 0 && (
                        <ol className='prec-list'>
                            {diseaseData.precautions.map((each, index) => (
                                <li key={index}>{each}</li>
                            ))}
                        </ol>
                    )}
                    <div className="other-stuff">
                        {diseaseData.drugs.length > 0 && (
                            diseaseData.drugs.map((drug, index) => (
                                <>
                                    <a href={diseaseData.drug_links[index]} target='_blank'>
                                        {drug}
                                    </a>
                                    <br />
                                </>
                            ))
                        )}
                    </div>
                </Modal.Body>
            </Modal>
        </div>
    )
};

export default Diagnosis;