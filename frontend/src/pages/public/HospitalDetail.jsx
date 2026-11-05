import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { usePageTitle } from "../../lib/usePageTitle";
import { MapPin, Search } from "lucide-react";
import { api, extractList } from "../../lib/api";
import DoctorCard from "../../components/DoctorCard";
import { Select, Input, Spinner } from "../../components/ui";

export default function HospitalDetail() {
  const { hospitalId } = useParams();
  const [hospital, setHospital] = useState(null);
  usePageTitle(hospital?.name || "Hospital"); 
  const [doctors, setDoctors] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [specializationId, setSpecializationId] = useState("");
  const [loading, setLoading] = useState(true);
const [nameQuery, setNameQuery] = useState("");


  useEffect(() => {
    api.get(`/hospitals/${hospitalId}`).then((res) => setHospital(res.data)).catch(() => {});
    api
      .get("/specializations")
      .then((res) => setSpecializations(extractList(res.data)))
      .catch(() => setSpecializations([]));
  }, [hospitalId]);

  useEffect(() => {
    setLoading(true);
    const params = { limit: 50 };
    if (specializationId) params.specialization_id = specializationId;
    api
      .get(`/hospitals/${hospitalId}/doctors`, { params })
      .then((res) => setDoctors(extractList(res.data)))
      .catch(() => setDoctors([]))
      .finally(() => setLoading(false));
  }, [hospitalId, specializationId]);

  const cleanedQuery = nameQuery.trim().toLowerCase().replace(/^dr\.?\s*/i, "");
  const filteredDoctors = doctors.filter((d) =>
    d.doctor_name.toLowerCase().includes(cleanedQuery)
  );
  
  if (!hospital) {
    return <div className="flex justify-center py-24 text-teal"><Spinner /></div>;
  }

  return (
    <div>
      <div className="h-56 w-full overflow-hidden bg-teal-light sm:h-72">
        {hospital.image_url ? (
          <img src={hospital.image_url} alt={hospital.name} className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center font-display text-5xl text-teal/40">
            {hospital.name?.[0]}
          </div>
        )}
      </div>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="font-display text-3xl font-semibold text-ink">{hospital.name}</h1>
        {hospital.address && (
          <p className="mt-2 flex items-center gap-1.5 text-slate">
            <MapPin size={16} /> {hospital.address}
          </p>
        )}

        <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-display text-xl font-semibold text-ink">Doctors here</h2>
          <div className="flex flex-wrap gap-3">
            <div className="relative">
              <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-light" />
              <Input
                value={nameQuery}
                onChange={(e) => setNameQuery(e.target.value)}
                placeholder="Search doctor by name"
                className="w-56 pl-9"
              />
            </div>
            <Select
              value={specializationId}
              onChange={(e) => setSpecializationId(e.target.value)}
              className="w-56"
            >
              <option value="">All specializations</option>
              {specializations.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </Select>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-16 text-teal"><Spinner /></div>
        ) : filteredDoctors.length === 0 ? (
          <p className="mt-8 text-slate">
            {nameQuery ? "No doctors match that name here." : "No doctors currently available here for this filter."}
          </p>
        ) : (
          <div className="mt-6 flex flex-col gap-4">
            {filteredDoctors.map((d) => (
              <DoctorCard
                key={d.doctor_hospital_id}
                doctor={{ ...d, hospital_id: hospital.id, hospital_name: hospital.name, hospital_address: hospital.address }}
                hospitalId={hospitalId}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}