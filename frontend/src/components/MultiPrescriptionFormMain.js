import React, { useState } from 'react';
import axios from 'axios';
import { Plus, X, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Multi-Medicine Prescription Form for Main Dashboard
export function MultiPrescriptionFormMain({ onClose, onSuccess, darkMode }) {
  const [formData, setFormData] = useState({
    patient_id: '',
    start_date: new Date().toISOString().split('T')[0],
    general_instructions: ""
  });
  const [medicines, setMedicines] = useState([
    { name: "", dosage: "", frequency: "", duration: "", notes: "" }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(false);

  // Fetch patients when component mounts
  React.useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    setLoadingPatients(true);
    try {
      const response = await axios.get(`${API}/patients/search?q=`);
      setPatients(response.data);
    } catch (error) {
      console.error("Failed to fetch patients:", error);
    } finally {
      setLoadingPatients(false);
    }
  };

  const addMedicine = () => {
    setMedicines([...medicines, { name: "", dosage: "", frequency: "", duration: "", notes: "" }]);
  };

  const removeMedicine = (index) => {
    if (medicines.length > 1) {
      setMedicines(medicines.filter((_, i) => i !== index));
    }
  };

  const updateMedicine = (index, field, value) => {
    const updatedMedicines = [...medicines];
    updatedMedicines[index][field] = value;
    setMedicines(updatedMedicines);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Validate patient selection
    if (!formData.patient_id) {
      setError("Please select a patient.");
      setLoading(false);
      return;
    }

    // Validate medicines
    const validMedicines = medicines.filter(med => med.name.trim() && med.dosage.trim() && med.frequency.trim());
    if (validMedicines.length === 0) {
      setError("Please add at least one complete medicine.");
      setLoading(false);
      return;
    }

    try {
      const prescriptionData = {
        patient_id: formData.patient_id,
        medicines: validMedicines,
        start_date: formData.start_date,
        general_instructions: formData.general_instructions
      };

      await axios.post(`${API}/multi-prescriptions`, prescriptionData);
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create prescription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`p-6 border rounded-lg mb-6 ${darkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-200 bg-gray-50'}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
          New Multi-Medicine Prescription
        </h3>
        <button onClick={onClose} className={`text-gray-500 hover:text-gray-700`}>
          <X className="h-5 w-5" />
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Patient Selection and General Information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
              Patient *
            </label>
            {loadingPatients ? (
              <div className="text-sm text-gray-500">Loading patients...</div>
            ) : (
              <select
                value={formData.patient_id}
                onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
                  darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
                }`}
                required
              >
                <option value="">Select a patient...</option>
                {patients.map((patient) => (
                  <option key={patient.user_id} value={patient.user_id}>
                    {patient.name} ({patient.email})
                  </option>
                ))}
              </select>
            )}
          </div>
          <div>
            <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
              Start Date
            </label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({...formData, start_date: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
                darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
              }`}
              required
            />
          </div>
          <div>
            <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
              General Instructions
            </label>
            <input
              type="text"
              value={formData.general_instructions}
              onChange={(e) => setFormData({...formData, general_instructions: e.target.value})}
              placeholder="General instructions for all medicines"
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500 ${
                darkMode ? 'bg-gray-600 border-gray-500 text-white' : 'bg-white border-gray-300'
              }`}
            />
          </div>
        </div>

        {/* Medicines Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h4 className={`text-md font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Medicines ({medicines.length})
            </h4>
            <button
              type="button"
              onClick={addMedicine}
              className="bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 flex items-center text-sm"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Medicine
            </button>
          </div>

          <div className="space-y-4">
            {medicines.map((medicine, index) => (
              <div key={index} className={`p-4 border rounded-lg ${darkMode ? 'border-gray-600 bg-gray-600' : 'border-gray-200 bg-white'}`}>
                <div className="flex items-center justify-between mb-3">
                  <h5 className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                    Medicine {index + 1}
                  </h5>
                  {medicines.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMedicine(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                  <div>
                    <label className={`block text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
                      Medicine Name *
                    </label>
                    <input
                      type="text"
                      value={medicine.name}
                      onChange={(e) => updateMedicine(index, 'name', e.target.value)}
                      placeholder="e.g., Aspirin"
                      className={`w-full px-2 py-1 text-sm border rounded focus:outline-none focus:border-blue-500 ${
                        darkMode ? 'bg-gray-700 border-gray-500 text-white' : 'bg-white border-gray-300'
                      }`}
                      required
                    />
                  </div>
                  <div>
                    <label className={`block text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
                      Dosage *
                    </label>
                    <input
                      type="text"
                      value={medicine.dosage}
                      onChange={(e) => updateMedicine(index, 'dosage', e.target.value)}
                      placeholder="e.g., 10mg, 2 tablets"
                      className={`w-full px-2 py-1 text-sm border rounded focus:outline-none focus:border-blue-500 ${
                        darkMode ? 'bg-gray-700 border-gray-500 text-white' : 'bg-white border-gray-300'
                      }`}
                      required
                    />
                  </div>
                  <div>
                    <label className={`block text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
                      Frequency *
                    </label>
                    <input
                      type="text"
                      value={medicine.frequency}
                      onChange={(e) => updateMedicine(index, 'frequency', e.target.value)}
                      placeholder="e.g., twice daily"
                      className={`w-full px-2 py-1 text-sm border rounded focus:outline-none focus:border-blue-500 ${
                        darkMode ? 'bg-gray-700 border-gray-500 text-white' : 'bg-white border-gray-300'
                      }`}
                      required
                    />
                  </div>
                  <div>
                    <label className={`block text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
                      Duration
                    </label>
                    <input
                      type="text"
                      value={medicine.duration}
                      onChange={(e) => updateMedicine(index, 'duration', e.target.value)}
                      placeholder="e.g., 7 days, 2 weeks"
                      className={`w-full px-2 py-1 text-sm border rounded focus:outline-none focus:border-blue-500 ${
                        darkMode ? 'bg-gray-700 border-gray-500 text-white' : 'bg-white border-gray-300'
                      }`}
                    />
                  </div>
                </div>

                <div className="mt-3">
                  <label className={`block text-xs font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} mb-1`}>
                    Notes
                  </label>
                  <input
                    type="text"
                    value={medicine.notes}
                    onChange={(e) => updateMedicine(index, 'notes', e.target.value)}
                    placeholder="Special instructions for this medicine"
                    className={`w-full px-2 py-1 text-sm border rounded focus:outline-none focus:border-blue-500 ${
                      darkMode ? 'bg-gray-700 border-gray-500 text-white' : 'bg-white border-gray-300'
                    }`}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex space-x-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center"
          >
            <Save className="h-4 w-4 mr-2" />
            {loading ? "Creating..." : "Create Prescription"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-600 text-white hover:bg-gray-500' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}`}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}