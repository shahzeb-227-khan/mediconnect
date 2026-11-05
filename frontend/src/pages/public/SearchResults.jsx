import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, extractList } from "../../lib/api";
import DoctorCard from "../../components/DoctorCard";
import { Select, Spinner, Button } from "../../components/ui";
import { usePageTitle } from "../../lib/usePageTitle";

const PAGE_SIZE = 10;

export default function SearchResults() {
  usePageTitle("Search Results");
  const [searchParams, setSearchParams] = useSearchParams();
  const [cities, setCities] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const cityId = searchParams.get("city_id") || "";
  const specializationId = searchParams.get("specialization_id") || "";
  const skip = parseInt(searchParams.get("skip") || "0", 10);

  useEffect(() => {
    api.get("/cities").then((res) => setCities(extractList(res.data))).catch(() => setCities([]));
    api
      .get("/specializations")
      .then((res) => setSpecializations(extractList(res.data)))
      .catch(() => setSpecializations([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = { skip, limit: PAGE_SIZE };
    if (cityId) params.city_id = cityId;
    if (specializationId) params.specialization_id = specializationId;

    api
      .get("/doctors/search", { params })
      .then((res) => {
        setResults(extractList(res.data));
        setTotal(typeof res.data?.total === "number" ? res.data.total : 0);
      })
      .catch(() => {
        setResults([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [cityId, specializationId, skip]);

  function updateParams(next) {
    const params = new URLSearchParams(searchParams);
    Object.entries(next).forEach(([k, v]) => {
      if (v) params.set(k, v);
      else params.delete(k);
    });
    if (!("skip" in next)) params.delete("skip");
    setSearchParams(params);
  }

  const page = Math.floor(skip / PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="font-display text-3xl font-semibold text-ink">Find a doctor</h1>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <Select value={cityId} onChange={(e) => updateParams({ city_id: e.target.value })} className="flex-1">
          <option value="">Any city</option>
          {cities.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </Select>
        <Select
          value={specializationId}
          onChange={(e) => updateParams({ specialization_id: e.target.value })}
          className="flex-1"
        >
          <option value="">Any specialization</option>
          {specializations.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </Select>
      </div>

      {loading ? (
        <div className="flex justify-center py-24 text-teal"><Spinner /></div>
      ) : results.length === 0 ? (
        <p className="mt-16 text-center text-slate">No doctors match this search yet.</p>
      ) : (
        <>
          <div className="mt-8 flex flex-col gap-4">
            {results.map((doctor) => (
              <div key={doctor.doctor_hospital_id}>
                <p className="mb-1.5 text-xs font-medium text-slate">
                  {doctor.hospital_name}
                  {doctor.hospital_address && <span className="font-normal text-slate-light"> · {doctor.hospital_address}</span>}
                </p>
                <DoctorCard doctor={doctor} hospitalId={doctor.hospital_id} />
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="mt-10 flex items-center justify-center gap-4">
              <Button
                variant="outline"
                disabled={page <= 1}
                onClick={() => updateParams({ skip: String(Math.max(0, skip - PAGE_SIZE)) })}
              >
                Previous
              </Button>
              <span className="text-sm text-slate">Page {page} of {totalPages}</span>
              <Button
                variant="outline"
                disabled={page >= totalPages}
                onClick={() => updateParams({ skip: String(skip + PAGE_SIZE) })}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}