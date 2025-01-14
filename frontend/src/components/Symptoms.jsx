import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import Diagnosis from './Diagnosis';
import { Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const Symptoms = () => {

  const [suggestions, loadSuggestions] = useState([]);
  const [chartData, setChartData] = useState({
    labels: [],
    points: []
  });

  const emptyData = {
    labels: [],
    points: []
  }

  const [ selectedList, setSelected ] = useState([]);

  const fetchSymptoms = async () => {
    const response = await fetch('http://localhost:5000/symptoms');
    const results = await response.json();

    if (!response.ok) {
        alert('Could not fetch symptoms');
        return;
    } 

    loadSuggestions(results.map((symptom) => ({
        value: symptom,
        label: capitalizeFirstLetter(symptom.replace(/_/g, ' ')) // replace underscores with spaces
    })));
  };

  const capitalizeFirstLetter = (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  };

  useEffect(() => {
    fetchSymptoms();
  }, []);

  const handleSelectChange = async (selected) => {
    setSelected(selected);

    if (selected.length === 0) {
      setChartData(emptyData)
      return;
    }

    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(selected.map(option => option.value))
    })
    const results = await response.json()
    // console.log(results)
    setChartData(transformData(results))
  };

  const remake = async () => {
    await fetch('http://localhost:5000/remake');
    handleSelectChange(selectedList);
  }

  const transformData = (data) => {
    const labels = data.map(item => item[0]);
    const values = data.map(item => item[1]);
    return { labels, points: values }
  }

  const startsWith = (option, input) => {
    return option.label.toLowerCase().startsWith(input.toLowerCase());
  };

  return (
    <>
      <div className='up-side'>
        <Select
          options={suggestions}
          onChange={handleSelectChange}
          isClearable
          isMulti
          placeholder="Select symptoms here"
          filterOption={startsWith}
        />
      </div>
        <Button variant="outline-light" className='refresh-button' onClick={remake}>
          <i className="bi bi-arrow-clockwise"></i> Refresh
        </Button>
      <div className='down-side'>
        <Diagnosis data={chartData} />
      </div>
    </>
  );
};

export default Symptoms;