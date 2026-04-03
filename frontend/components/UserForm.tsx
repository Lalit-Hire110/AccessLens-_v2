"use client";

import { useState } from "react";
import type { UserInput } from "@/lib/api";

// ---------------------------------------------------------------------------
// Select options
// ---------------------------------------------------------------------------

const GENDER_OPTIONS = ["male", "female"];
const RURAL_URBAN_OPTIONS = ["rural", "urban"];
const INCOME_OPTIONS = ["low", "middle", "high"];
const OCCUPATION_OPTIONS = [
  "worker",
  "farmer",
  "student",
  "self-employed",
  "unemployed",
];
const EDUCATION_OPTIONS = ["none", "primary", "secondary", "graduate"];
const DIGITAL_OPTIONS = ["none", "limited", "full"];
const INSTITUTIONAL_OPTIONS = ["low", "medium", "high"];

// ---------------------------------------------------------------------------
// Default form state
// ---------------------------------------------------------------------------

const DEFAULT_FORM: UserInput = {
  age: 26,
  gender: "male",
  rural_urban: "urban",
  income_level: "middle",
  occupation: "worker",
  education_level: "graduate",
  digital_access: "full",
  document_completeness: 0.75,
  institutional_dependency: "low",
  top_k: 5,
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const inputClass =
  "w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-gray-100 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500";

const labelClass = "text-sm font-medium text-gray-300";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  onSubmit: (data: UserInput) => void;
  loading: boolean;
}

export default function UserForm({ onSubmit, loading }: Props) {
  const [form, setForm] = useState<UserInput>(DEFAULT_FORM);

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "number" ? (value === "" ? "" : Number(value)) : value,
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit(form);
  }

  function renderSelect(
    label: string,
    name: keyof UserInput,
    options: string[]
  ) {
    return (
      <div className="flex flex-col gap-1">
        <label htmlFor={name} className={labelClass}>
          {label}
        </label>
        <select
          id={name}
          name={name}
          value={form[name] as string}
          onChange={handleChange}
          className={inputClass}
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt.charAt(0).toUpperCase() + opt.slice(1)}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-lg"
    >
      <h2 className="mb-5 text-lg font-semibold text-gray-100">
        User Profile
      </h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Age */}
        <div className="flex flex-col gap-1">
          <label htmlFor="age" className={labelClass}>
            Age
          </label>
          <input
            id="age"
            name="age"
            type="number"
            min={0}
            max={150}
            value={form.age}
            onChange={handleChange}
            className={inputClass}
          />
        </div>

        {renderSelect("Gender", "gender", GENDER_OPTIONS)}
        {renderSelect("Area", "rural_urban", RURAL_URBAN_OPTIONS)}
        {renderSelect("Income Level", "income_level", INCOME_OPTIONS)}
        {renderSelect("Occupation", "occupation", OCCUPATION_OPTIONS)}
        {renderSelect("Education Level", "education_level", EDUCATION_OPTIONS)}
        {renderSelect("Digital Access", "digital_access", DIGITAL_OPTIONS)}

        {/* Document Completeness */}
        <div className="flex flex-col gap-1">
          <label htmlFor="document_completeness" className={labelClass}>
            Doc. Completeness (0–1)
          </label>
          <input
            id="document_completeness"
            name="document_completeness"
            type="number"
            min={0}
            max={1}
            step={0.05}
            value={form.document_completeness as number}
            onChange={handleChange}
            className={inputClass}
          />
        </div>

        {renderSelect(
          "Institutional Dependency",
          "institutional_dependency",
          INSTITUTIONAL_OPTIONS
        )}

        {/* Top K */}
        <div className="flex flex-col gap-1">
          <label htmlFor="top_k" className={labelClass}>
            Top K Results
          </label>
          <input
            id="top_k"
            name="top_k"
            type="number"
            min={1}
            max={50}
            value={form.top_k ?? 5}
            onChange={handleChange}
            className={inputClass}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-6 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
      >
        {loading ? "Running…" : "Get Recommendations"}
      </button>
    </form>
  );
}
