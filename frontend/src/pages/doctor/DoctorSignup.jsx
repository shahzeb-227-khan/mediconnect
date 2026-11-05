import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useDoctorAuth } from "../../context/DoctorAuthContext";
import { api, extractList, extractErrorMessage } from "../../lib/api";
import { Button, Input, Select, TextArea, Alert } from "../../components/ui";
import { usePageTitle } from "../../lib/usePageTitle";

export default function DoctorSignup() {
  usePageTitle("Doctor Sign Up");
  const { signup } = useDoctorAuth();
  const [specializations, setSpecializations] = useState([]);
  const [form, setForm] = useState({
    email: "",
    password: "",
    name: "",
    specialization_id: "",
    qualifications: "",
    experience_years: "",
    bio: "",
  });
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api
      .get("/specializations")
      .then((res) => setSpecializations(extractList(res.data)))
      .catch(() => setSpecializations([]));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup({
        ...form,
        specialization_id: parseInt(form.specialization_id, 10),
        experience_years: form.experience_years ? parseInt(form.experience_years, 10) : undefined,
        qualifications: form.qualifications || undefined,
        bio: form.bio || undefined,
      });
      setDone(true);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="mx-auto max-w-md px-6 py-24 text-center">
        <h1 className="font-display text-2xl font-semibold text-ink">Check your inbox</h1>
        <p className="mt-3 text-slate">
          We've sent a verification link to <strong>{form.email}</strong>. Verify your email, then log in — you can
          complete your profile and apply to hospitals afterward.
        </p>
        <Link to="/doctor/login" className="mt-6 inline-block font-medium text-teal">Go to login</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="font-display text-2xl font-semibold text-ink">Join as a doctor</h1>
      <p className="mt-1 text-sm text-slate">
        Reach patients directly. Your profile is reviewed before your hospital applications go live.
      </p>

      {error && <div className="mt-4"><Alert>{error}</Alert></div>}

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <Input label="Full name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Aftab Hussain" />
        <Input label="Email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <Select
          label="Specialization"
          required
          value={form.specialization_id}
          onChange={(e) => setForm({ ...form, specialization_id: e.target.value })}
        >
          <option value="">Select your specialization</option>
          {specializations.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </Select>
        <Input
          label="Qualifications (optional)"
          value={form.qualifications}
          onChange={(e) => setForm({ ...form, qualifications: e.target.value })}
          placeholder="e.g. MBBS, FCPS"
        />
        <Input
          label="Years of experience (optional)"
          type="number"
          min="0"
          value={form.experience_years}
          onChange={(e) => setForm({ ...form, experience_years: e.target.value })}
        />
        <TextArea
          label="Bio (optional)"
          rows={3}
          value={form.bio}
          onChange={(e) => setForm({ ...form, bio: e.target.value })}
        />
        <Input
          label="Password"
          type="password"
          required
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <p className="text-xs text-slate-light">At least 8 characters, one number, one uppercase letter.</p>
        <Button type="submit" disabled={loading} className="mt-2 justify-center">
          {loading ? "Creating account..." : "Sign up"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate">
        Already registered? <Link to="/doctor/login" className="font-medium text-teal">Log in</Link>
      </p>
    </div>
  );
}
