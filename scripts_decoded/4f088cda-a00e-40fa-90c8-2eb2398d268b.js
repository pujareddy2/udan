// UDAAN AI — the comprehensive profile schema (single source of truth).
// Both the read-only Profile sheet and the editable Profile Builder render
// from this. No demo values live here: everything is filled by the user.
window.UDAAN_PROFILE_SCHEMA = (function () {
  const common = [
    { id: "identity", title: "Basic Information", icon: "award", fields: [
      { key: "full_name", label: "Full Name", type: "text" },
      { key: "mobile_number", label: "Mobile Number", type: "tel" },
      { key: "email", label: "Email", type: "email" },
      { key: "date_of_birth", label: "Date of Birth", type: "date" },
      { key: "gender", label: "Gender", type: "select", options: ["Female", "Male", "Other"] }
    ]},
    { id: "location", title: "Location Information", icon: "globe", fields: [
      { key: "state", label: "State", type: "text" },
      { key: "district", label: "District", type: "text" },
      { key: "city", label: "City", type: "text" }
    ]},
    { id: "social", title: "Social Information", icon: "shield", fields: [
      { key: "category", label: "Category", type: "select", options: ["General", "OBC", "SC", "ST", "EWS"] },
      { key: "annual_family_income", label: "Annual Family Income", type: "text" },
      { key: "family_size", label: "Family Size", type: "number" },
      { key: "special_category", label: "Special Category", type: "select", options: ["None", "Minority", "PwD", "Single Parent", "Orphan", "Defence Family"] }
    ]}
  ];

  const personas = {
    students: [
      { id: "documents_available", title: "Documents Available", icon: "book", type: "multi",
        hint: "Select the documents you currently have.",
        options: ["Aadhaar", "Student ID", "Bonafide", "Income Certificate", "Caste Certificate", "EWS Certificate", "Marksheets"] },
      { id: "opportunity_interests", title: "Opportunity Interests", icon: "spark", type: "multi",
        hint: "Select the opportunities you are interested in.",
        options: ["Scholarships", "Internships", "Research Programs", "Hackathons", "Fellowships", "Training Programs", "Government Schemes"] },
      { id: "academic", title: "Academic Information", icon: "award", fields: [
        { key: "college_name", label: "College", type: "text" },
        { key: "university_name", label: "University", type: "text" },
        { key: "degree", label: "Degree", type: "text" },
        { key: "branch", label: "Branch", type: "text" },
        { key: "specialization", label: "Specialization", type: "text" },
        { key: "current_year", label: "Current Year", type: "text" },
        { key: "graduation_year", label: "Graduation Year", type: "text" },
        { key: "cgpa", label: "CGPA", type: "text" },
        { key: "percentage", label: "Percentage", type: "text" }
      ]},
      { id: "education_background", title: "Education Background", icon: "book", fields: [
        { key: "tenth_percentage", label: "10th %", type: "text" },
        { key: "twelfth_percentage", label: "12th %", type: "text" },
        { key: "diploma_percentage", label: "Diploma %", type: "text" }
      ]},
      { id: "skills", title: "Skills", icon: "chart", type: "multi",
        hint: "Select your core skills.",
        options: ["Programming", "AI/ML", "Data Science", "Cloud", "Cybersecurity", "Web Development", "Mobile Development", "UI/UX", "IoT", "Robotics", "Communication", "Research", "Leadership"] },
      { id: "achievements", title: "Achievements", icon: "shield", type: "multi",
        hint: "Select your achievements.",
        options: ["Certifications", "Hackathons", "Projects", "Research Papers"] },
      { id: "career_goals", title: "Career Goals", icon: "coin", type: "multi",
        hint: "Select your career goals.",
        options: ["Higher Studies", "Government Job", "Private Job", "Startup", "Research", "Foreign Education"] }
    ],
    farmers: [
      { id: "documents_available", title: "Documents Available", icon: "book", type: "multi",
        hint: "Select the documents you currently have.",
        options: ["Aadhaar", "Income Certificate", "Caste Certificate", "Bank Account", "Land Passbook"] },
      { id: "digital", title: "Digital Readiness", icon: "spark", type: "bool",
        hint: "What do you have access to?",
        fields: [
          { key: "smartphone_available", label: "Smartphone" },
          { key: "internet_access", label: "Internet Access" }
        ]},
      { id: "land", title: "Land Information", icon: "sprout", fields: [
        { key: "owns_land", label: "Owns Land", type: "select", options: ["Yes", "No"] },
        { key: "land_area", label: "Land Area", type: "number" },
        { key: "land_unit", label: "Land Unit", type: "select", options: ["Acres", "Hectares"] },
        { key: "land_type", label: "Land Type", type: "select", options: ["Irrigated", "Rainfed"] },
        { key: "land_ownership", label: "Land Ownership", type: "select", options: ["Self", "Lease", "Both"] }
      ]},
      { id: "farm", title: "Farm Details", icon: "chart", fields: [
        { key: "crop_type", label: "Crop Type", type: "text" },
        { key: "farming_type", label: "Farming Type", type: "select", options: ["Crop", "Dairy", "Poultry", "Fishery", "Mixed"] },
        { key: "livestock", label: "Livestock", type: "text" }
      ]},
      { id: "farmer_status", title: "Farmer Status", icon: "shield", type: "bool",
        hint: "Tick what applies to you.",
        fields: [
          { key: "farmer_registration", label: "Farmer Registration" },
          { key: "pm_kisan_enrolled", label: "PM-Kisan Enrolled" },
          { key: "kisan_credit_card", label: "Kisan Credit Card" },
          { key: "crop_insurance", label: "Crop Insurance" }
        ]},
      { id: "farmer_financial", title: "Financial Details", icon: "coin", fields: [
        { key: "annual_income", label: "Annual Income", type: "text" },
        { key: "existing_loan", label: "Existing Loan", type: "select", options: ["Yes", "No"] },
        { key: "loan_amount", label: "Loan Amount", type: "text" },
        { key: "bank_account", label: "Bank Account", type: "select", options: ["Yes", "No"] }
      ]}
    ],
    jobseekers: [
      { id: "documents_available", title: "Documents Available", icon: "book", type: "multi",
        hint: "Select the documents you currently have.",
        options: ["Aadhaar", "Income Certificate", "Caste Certificate", "Bank Account", "PAN", "Ration Card"] },
      { id: "digital", title: "Digital Readiness", icon: "spark", type: "bool",
        hint: "What do you have access to?",
        fields: [
          { key: "smartphone_available", label: "Smartphone" },
          { key: "internet_access", label: "Internet Access" }
        ]},
      { id: "js_education", title: "Education", icon: "book", fields: [
        { key: "qualification", label: "Qualification", type: "text" },
        { key: "experience_years", label: "Experience (years)", type: "text" }
      ]}
    ]
  };

  return { common: common, personas: personas };
})();

