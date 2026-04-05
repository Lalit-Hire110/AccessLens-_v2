"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import type { UserInput } from "@/lib/api";
import { hoverButton } from "@/lib/motion";

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
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const inputClass = "input";

const labelClass = "text-sm font-medium text-content-secondary mb-1.5 block";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface Props {
  onSubmit: (data: UserInput) => void;
  loading: boolean;
  initialValues?: UserInput;
}

export default function UserForm({ onSubmit, loading, initialValues }: Props) {
  const [form, setForm] = useState<UserInput>(initialValues ?? DEFAULT_FORM);

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
      <div key={name} className="flex flex-col">
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
      className="card p-6 space-y-6"
    >
      <h2 className="text-xl font-semibold text-content-primary">
        User Profile
      </h2>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {/* Age */}
        <div className="flex flex-col">
          <label htmlFor="age" className={labelClass}>Age</label>
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
        <div className="flex flex-col">
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
      </div>

      <motion.button
        type="submit"
        disabled={loading}
        {...hoverButton}
        className="btn btn-primary w-full sm:w-auto"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
            Analysing…
          </span>
        ) : (
          "Get Recommendations"
        )}
      </motion.button>
    </form>
  );
}
