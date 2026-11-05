import { useEffect, useState } from "react";
import { usePageTitle } from "../../lib/usePageTitle";
import { useSearchParams } from "react-router-dom";
import { Search } from "lucide-react";
import { api, extractList } from "../../lib/api";
import HospitalCard from "../../components/HospitalCard";
import { Select, Spinner, Button } from "../../components/ui";

const PAGE_SIZE = 12;

export default function HospitalsList() {
  usePageTitle("Find Hospitals");
  const [searchParams, setSearchParams] = useSearchParams();
  const [cities, setCities] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(searchParams.get("search") || "");

  const cityId = searchParams.get("city_id") || "";
  const skip = parseInt(searchParams.get("skip") || "0", 10);

  useEffect(() => {
    api.get("/cities").then((res) => setCities(extractList(res.data))).catch(() => setCities([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = { skip, limit: PAGE_SIZE };
    if (cityId) params.city_id = cityId;
    if (searchParams.get("search")) params.search = searchParams.get("search");

    api
      .get("/hospitals", { params })
      .then((res) => {
        setHospitals(extractList(res.data));
        setTotal(typeof res.data?.total === "number" ? res.data.total : 0);
      })
      .catch(() => {
        setHospitals([]);
        setTotal(0);
      })
      .finally(() => setLoading(false));
  }, [cityId, skip, searchParams]);

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
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="font-display text-3xl font-semibold text-ink">Find a hospital</h1>
      <p className="mt-1 text-slate">Browse hospitals and see which doctors are available at each.</p>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <form
          className="flex flex-1 gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            updateParams({ search });
          }}
        >
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-light" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search hospital name..."
              className="w-full rounded-xl border border-slate-light/50 py-2.5 pl-10 pr-4 text-sm outline-none focus:border-teal"
            />
          </div>
          <Button type="submit" variant="outline">Search</Button>
        </form>

        <Select value={cityId} onChange={(e) => updateParams({ city_id: e.target.value })} className="sm:w-56">
          <option value="">All cities</option>
          {cities.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </Select>
      </div>

      {loading ? (
        <div className="flex justify-center py-24 text-teal"><Spinner /></div>
      ) : hospitals.length === 0 ? (
        <p className="mt-16 text-center text-slate">No hospitals found. Try a different search.</p>
      ) : (
        <>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {hospitals.map((h) => (
              <HospitalCard key={h.id} hospital={h} />
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
