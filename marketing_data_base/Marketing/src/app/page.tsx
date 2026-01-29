import Link from "next/link";

export default function Home() {
  return (
    <main className="container">
      <h1 className="heading">Job Management</h1>

      <div className="grid-3">
        {/* Option 1: Fill New Entry */}
        <Link href="/fillin" className="card flex-center" style={{ flexDirection: 'column', gap: '1rem', textDecoration: 'none' }}>
          <div style={{ fontSize: '2rem' }}>📝</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Fill New Entry</h2>
          <p style={{ color: '#a1a1aa', textAlign: 'center' }}>Add a new staffing requirement</p>
        </Link>

        {/* Option 2: View Existing Details */}
        <Link href="/existing" className="card flex-center" style={{ flexDirection: 'column', gap: '1rem', textDecoration: 'none', cursor: 'pointer' }}>
          <div style={{ fontSize: '2rem' }}>📂</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Existing Details</h2>
          <p style={{ color: '#a1a1aa', textAlign: 'center' }}>View and manage current list</p>
        </Link>

        {/* Option 3: Show Active/Inactive Toggle */}
        <div className="card flex-center" style={{ flexDirection: 'column', gap: '1rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Filter Status</h2>

          <div className="switch-wrapper">
            <div className="flex-center" style={{ gap: '0.5rem' }}>
              <div className="status-indicator"></div>
              <span>Active</span>
            </div>

            <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '48px', height: '24px' }}>
              <input type="checkbox" defaultChecked style={{ opacity: 0, width: 0, height: 0 }} />
              <span style={{ position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#3f3f46', transition: '.4s', borderRadius: '34px' }}></span>
              <span style={{ position: 'absolute', content: '""', height: '16px', width: '16px', left: '4px', bottom: '4px', backgroundColor: 'white', transition: '.4s', borderRadius: '50%', transform: 'translateX(24px)' }}></span>
            </label>

            <div className="flex-center" style={{ gap: '0.5rem' }}>
              <div className="status-indicator inactive"></div>
              <span>Inactive</span>
            </div>
          </div>
          <p style={{ color: '#a1a1aa', fontSize: '0.8rem' }}>Toggle to show inactive records</p>
        </div>
      </div>
    </main>
  );
}
