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
      { key: "village_city", label: "Village/Town", type: "text" },
      { key: "urban_or_rural", label: "Rural / Urban", type: "select", options: ["Urban", "Rural"] }
    ]},
    { id: "social", title: "Social Information", icon: "shield", fields: [
      { key: "category", label: "Category", type: "select", options: ["General", "OBC", "SC", "ST", "EWS"] },
      { key: "annual_family_income", label: "Annual Family Income", type: "text" },
      { key: "family_size", label: "Family Size", type: "number" },
      { key: "special_category", label: "Special Category", type: "select", options: ["None", "Minority", "PwD", "Widow", "Single Woman", "Veteran Family"] }
    ]},
    { id: "documents_available", title: "Documents Available", icon: "book", type: "multi",
      hint: "Select the documents you currently have.",
      options: ["Aadhaar", "PAN", "Income Certificate", "Caste Certificate", "Ration Card", "Bank Account", "Land Passbook", "Graduation Certificate", "Intermediate Certificate"] },
    { id: "digital", title: "Digital Readiness", icon: "spark", type: "bool",
      hint: "What do you have access to?",
      fields: [
        { key: "smartphone_available", label: "Smartphone" },
        { key: "internet_access", label: "Internet Access" },
        { key: "digital_payment_access", label: "Digital Payments" },
      ]}
  ];

  const personas = {
    students: [
      { id: "academic", title: "Academic Information", icon: "award", fields: [
        { key: "college_name", label: "College", type: "text" },
        { key: "university_name", label: "University", type: "text" },
        { key: "degree", label: "Degree", type: "text" },
        { key: "branch", label: "Branch", type: "text" },
        { key: "current_year", label: "Current Year", type: "text" },
        { key: "cgpa", label: "CGPA", type: "text" }
      ]}
    ],
    farmers: [
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
      { id: "js_education", title: "Education & Experience", icon: "book", fields: [
        { key: "qualification", label: "Highest Qualification", type: "text" },
        { key: "experience_years", label: "Experience (years)", type: "text" },
        { key: "preferred_job_role", label: "Preferred Job Role", type: "text" },
        { key: "employment_status", label: "Employment Status", type: "select",
          options: ["Student", "Unemployed", "Employed", "Career Switcher"] }
      ]},
      { id: "js_skills", title: "Skills", icon: "spark", type: "multi", customInput: true,
        hint: "Select your current skills. These help match you with skilling schemes and job opportunities.",
        options: [
          "Python", "SQL", "JavaScript", "Java", "HTML/CSS", "C/C++",
          "Data Analysis", "MS Office", "Tally / Accounting",
          "Communication (English)", "Communication (Hindi)",
          "Leadership", "Customer Service",
          "Electrical Wiring", "Plumbing", "Welding / Fabrication",
          "Tailoring / Textile", "Beauty & Wellness",
          "Mobile Repair", "Computer Hardware"
        ]
      },
      { id: "js_career_target", title: "Career Target", icon: "briefcase", fields: [
        { key: "target_sector", label: "Target Sector", type: "select",
          options: ["Government / Public Sector", "IT / Software", "Banking / Finance",
                    "Healthcare", "Manufacturing", "Teaching / Education",
                    "Defence / Police", "Retail / Sales", "Other"] },
        { key: "preferred_job_type", label: "Preferred Job Type", type: "select",
          options: ["Full-time", "Part-time", "Apprenticeship", "Internship", "Freelance"] }
      ]}
    ],
  };

  return { common: common, personas: personas };
})();
