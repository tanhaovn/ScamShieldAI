function DatasetPage({ categories, form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return (
    <section className="panel">
      <h3>Training dataset</h3>
      <form onSubmit={onSubmit} className="admin-form">
        <input
          value={form.image_url}
          onChange={(event) =>
            setForm({ ...form, image_url: event.target.value })
          }
          placeholder="image_url"
        />
        <select
          value={form.scam_category_id}
          onChange={(event) =>
            setForm({ ...form, scam_category_id: event.target.value })
          }
        >
          <option value="">{en ? "Choose category" : "Chọn danh mục"}</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.display_name}
            </option>
          ))}
        </select>
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.is_anonymized}
            onChange={(event) =>
              setForm({ ...form, is_anonymized: event.target.checked })
            }
          />
          Anonymized
        </label>
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.is_verified}
            onChange={(event) =>
              setForm({ ...form, is_verified: event.target.checked })
            }
          />
          Verified
        </label>
        <button type="submit">{en ? "Add dataset" : "Thêm dataset"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No datasets yet" : "Chưa có dataset"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.scam_category_id}</span>
            <strong>{item.is_verified ? "Verified" : "Pending"}</strong>
            <small>{item.uploaded_by}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function ModelsPage({ form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return (
    <section className="panel">
      <h3>AI models</h3>
      <form onSubmit={onSubmit} className="admin-form">
        <input
          value={form.version_name}
          onChange={(event) =>
            setForm({ ...form, version_name: event.target.value })
          }
          placeholder="version_name"
        />
        <input
          value={form.description}
          onChange={(event) =>
            setForm({ ...form, description: event.target.value })
          }
          placeholder="description"
        />
        <label className="check-row">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(event) =>
              setForm({ ...form, is_active: event.target.checked })
            }
          />
          Active
        </label>
        <button type="submit">{en ? "Add model" : "Thêm mô hình"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No models yet" : "Chưa có mô hình"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.version_name}</span>
            <strong>{item.is_active ? "Active" : "Inactive"}</strong>
            <small>{new Date(item.created_at).toLocaleDateString()}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function EvaluationsPage({ form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  const fields = [
    "ai_model_id",
    "macro_f1",
    "recall",
    "false_alarm_rate",
    "explanation_usefulness",
  ];
  return (
    <section className="panel">
      <h3>Model evaluations</h3>
      <form onSubmit={onSubmit} className="admin-form">
        {fields.map((field) => (
          <input
            key={field}
            type="number"
            step={field === "ai_model_id" ? undefined : "0.01"}
            value={form[field]}
            onChange={(event) =>
              setForm({ ...form, [field]: event.target.value })
            }
            placeholder={field}
          />
        ))}
        <button type="submit">{en ? "Save evaluation" : "Lưu đánh giá"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No evaluations yet" : "Chưa có đánh giá"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>Model #{item.ai_model_id}</span>
            <strong>F1 {item.macro_f1}</strong>
            <small>Recall {item.recall}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

function LogsPage({ form, setForm, onSubmit, items, language }) {
  const en = language === "en";
  return (
    <section className="panel">
      <h3>System activity logs</h3>
      <form onSubmit={onSubmit} className="admin-form">
        <input
          value={form.action_type}
          onChange={(event) =>
            setForm({ ...form, action_type: event.target.value })
          }
          placeholder="action_type"
        />
        <input
          value={form.description}
          onChange={(event) =>
            setForm({ ...form, description: event.target.value })
          }
          placeholder="description"
        />
        <button type="submit">{en ? "Add log" : "Ghi nhật ký"}</button>
      </form>
      <ul className="list">
        {items.length === 0 && <li>{en ? "No logs yet" : "Chưa có nhật ký"}</li>}
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.action_type}</span>
            <strong>{item.admin_id}</strong>
            <small>{item.description}</small>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function AdminPage({
  activePage,
  categories,
  datasetForm,
  setDatasetForm,
  handleCreateDataset,
  datasets,
  modelForm,
  setModelForm,
  handleCreateModel,
  models,
  evaluationForm,
  setEvaluationForm,
  handleCreateEvaluation,
  evaluations,
  logForm,
  setLogForm,
  handleCreateLog,
  logs,
  language = "vi",
}) {
  const pages = {
    "admin-dataset": (
      <DatasetPage
        categories={categories}
        form={datasetForm}
        setForm={setDatasetForm}
        onSubmit={handleCreateDataset}
        items={datasets}
        language={language}
      />
    ),
    "admin-models": (
      <ModelsPage
        form={modelForm}
        setForm={setModelForm}
        onSubmit={handleCreateModel}
        items={models}
        language={language}
      />
    ),
    "admin-evaluations": (
      <EvaluationsPage
        form={evaluationForm}
        setForm={setEvaluationForm}
        onSubmit={handleCreateEvaluation}
        items={evaluations}
        language={language}
      />
    ),
    "admin-logs": (
      <LogsPage
        form={logForm}
        setForm={setLogForm}
        onSubmit={handleCreateLog}
        items={logs}
        language={language}
      />
    ),
  };
  return <div className="admin-grid">{pages[activePage]}</div>;
}
