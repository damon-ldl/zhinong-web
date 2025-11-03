import React, { useMemo, useState } from 'react';
import mammoth from 'mammoth/mammoth.browser';
import '../../assets/styles/login.scss';
import { analyzeDocument } from '../../request/index';

const Login = () => {
  // 全局场景/视图
  const [currentView, setCurrentView] = useState('review'); // 'review' | 'dashboard'
  const [currentScene, setCurrentScene] = useState('scene1'); // scene1: 作业指导书, scene2: 高后果区
  const [isDragging, setIsDragging] = useState(false);
  const [temperatureValue, setTemperatureValue] = useState('0.5');
  const [originalContent, setOriginalContent] = useState('');
  const [selectedFilePath, setSelectedFilePath] = useState('');
  const [fileUrl, setFileUrl] = useState(null);
  const [aiResult, setAiResult] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  // 仪表盘模拟数据
  const dashboardStats = useMemo(() => ({
    todayTasks: 128,
    recentTasks: 864,
    avgTimeSec: 92,
    successRate: 0.93,
    f1Score: 0.90,
    accuracy: 0.94,
  }), []);
  const [alerts, setAlerts] = useState([
    { id: 'a1', scene: 'scene1', title: '模板不匹配', time: '10:21', retriable: true },
    { id: 'a2', scene: 'scene2', title: 'OCR 失败', time: '09:58', retriable: true },
    { id: 'a3', scene: 'scene1', title: '命名规范告警', time: '08:40', retriable: false },
  ]);
  const retryAlert = (id) => {
    setAlerts(prev => prev.map(x => x.id === id ? { ...x, retriable: false } : x));
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      // 浏览器不提供真实本地路径，这里记录文件名与大小
      const sizeKB = file.size ? ` · ${(file.size/1024).toFixed(1)} KB` : '';
      setSelectedFilePath(`(拖拽) ${file.name}${sizeKB}`);
      if (fileUrl) {
        try { URL.revokeObjectURL(fileUrl); } catch (e) { /* ignore */ }
      }
      setFileUrl(URL.createObjectURL(file));
      handleFileRead(file);
    }
  };
  
  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      const file = files[0];
      const sizeKB = file.size ? ` · ${(file.size/1024).toFixed(1)} KB` : '';
      // e.target.value 在浏览器中通常是 C:\\fakepath\\filename.ext
      const inputPath = e.target.value || file.name;
      setSelectedFilePath(`${inputPath}${sizeKB}`);
      if (fileUrl) {
        try { URL.revokeObjectURL(fileUrl); } catch (e2) { /* ignore */ }
      }
      setFileUrl(URL.createObjectURL(file));
      handleFileRead(file);
    }
  };

  const handleFileRead = (file) => {
    const fileName = file.name.toLowerCase();
    const isText = file.type.startsWith('text/') || fileName.endsWith('.txt');

    if (isText) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const content = evt.target.result || '';
        setOriginalContent(String(content));
      };
      reader.onerror = () => {
        setOriginalContent('读取文本失败，请重试。');
      };
      reader.readAsText(file, 'utf-8');
      return;
    }

    // 解析 .docx 原文内容
    if (fileName.endsWith('.docx')) {
      const reader = new FileReader();
      reader.onload = async (evt) => {
        try {
          const arrayBuffer = evt.target.result;
          const result = await mammoth.convertToHtml({ arrayBuffer });
          const html = result.value || '';
          const text = html
            .replace(/<\/(p|div|h\d|li)>/gi, '\n')
            .replace(/<br\s*\/?>/gi, '\n')
            .replace(/<[^>]+>/g, '')
            .replace(/\u00A0/g, ' ')
            .trim();
          setOriginalContent(text);
        } catch (err) {
          setOriginalContent('读取 .docx 失败，请重试或转换为 .txt 后上传。');
        }
      };
      reader.onerror = () => {
        setOriginalContent('读取 .docx 失败，请重试。');
      };
      reader.readAsArrayBuffer(file);
      return;
    }

    // 非纯文本文件暂不做内容解析，给出提示
    if (fileName.endsWith('.pdf')) {
      setOriginalContent('已上传 PDF：暂不支持直接预览原文，请上传 .txt 查看原文内容。');
    } else if (fileName.endsWith('.doc')) {
      setOriginalContent('已上传 .doc（老版 Word）：浏览器端不易解析，建议转为 .docx 或 .txt。');
    } else if (file.type.startsWith('image/')) {
      setOriginalContent('已上传图片：暂不支持提取原文文本，请上传 .txt 文件。');
    } else {
      setOriginalContent('该文件类型暂不支持原文预览。');
    }
  };
  
  const handleTemperatureChange = (e) => {
    setTemperatureValue(e.target.value);
  };

  const handleAnalyze = async () => {
    if (!selectedFilePath) return;
    setSubmitting(true);
    setAiResult('');
    try {
      const res = await analyzeDocument({ path: selectedFilePath, temperature: Number(temperatureValue) });
      const data = res?.data || {};
      if (data.code === 200) {
        setAiResult(data.result || '');
      } else {
        setAiResult(data.message || '分析失败');
      }
    } catch (err) {
      setAiResult('请求失败，请稍后重试');
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <div className='login'>
      {/* 顶部导航（仅此文件内的轻量实现） */}
      <div style={{ position: 'fixed', top: 12, left: 20, right: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 10 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {[
            { key: 'dashboard', label: '仪表盘' },
            { key: 'review', label: '文档审核' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setCurrentView(tab.key)}
              style={{
                padding: '8px 14px',
                borderRadius: 999,
                border: '1px solid #dbe3f0',
                background: currentView === tab.key ? '#1890ff' : '#ffffff',
                color: currentView === tab.key ? '#fff' : '#1f2937',
                cursor: 'pointer'
              }}
            >{tab.label}</button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {[
            { key: 'scene1', label: '场景一：作业指导书 AI 审核' },
            { key: 'scene2', label: '场景二：高后果区风险管控 AI 审核' },
          ].map(scene => (
            <button
              key={scene.key}
              onClick={() => setCurrentScene(scene.key)}
              style={{
                padding: '8px 12px',
                borderRadius: 8,
                border: '1px solid #dbe3f0',
                background: currentScene === scene.key ? '#e6f4ff' : '#fff',
                color: '#1890ff',
                cursor: 'pointer'
              }}
            >{scene.label}</button>
          ))}
        </div>
      </div>

      {/* 左右区域复用，根据视图切换内容 */}
      {currentView === 'dashboard' && (
        <>
          <div className='background'>
            <div className="uploadContainer">
              <div className="uploadTitle"><h1>概览</h1></div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
                {[{ label: '今日任务', value: dashboardStats.todayTasks }, { label: '最近任务', value: dashboardStats.recentTasks }, { label: '平均审核时长', value: `${dashboardStats.avgTimeSec}s` }, { label: '成功率', value: `${Math.round(dashboardStats.successRate*100)}%` }].map(x => (
                  <div key={x.label} style={{ padding: 14, border: '1px solid rgba(0,0,0,0.06)', borderRadius: 12, background: '#fff' }}>
                    <div style={{ color: '#64748b', fontSize: 12 }}>{x.label}</div>
                    <div style={{ fontSize: 22, fontWeight: 800, color: '#0f172a' }}>{x.value}</div>
                  </div>
                ))}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12, marginTop: 12 }}>
                {[{ label: 'F1', value: `${Math.round(dashboardStats.f1Score*100)}%` }, { label: '准确率', value: `${Math.round(dashboardStats.accuracy*100)}%` }].map(x => (
                  <div key={x.label} style={{ padding: 14, border: '1px solid rgba(0,0,0,0.06)', borderRadius: 12, background: '#fff' }}>
                    <div style={{ color: '#64748b', fontSize: 12 }}>{x.label}</div>
                    <div style={{ fontSize: 22, fontWeight: 800, color: '#0f172a' }}>{x.value}</div>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 16 }}>
                <div className="uploadTitle"><h1>最近告警/失败任务</h1></div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {alerts.map(item => (
                    <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid #eef2f7', padding: '10px 12px', borderRadius: 10 }}>
                      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                        <span style={{ fontSize: 12, color: '#64748b' }}>{item.time}</span>
                        <span style={{ fontWeight: 600 }}>{item.title}</span>
                        <span style={{ fontSize: 12, color: '#1890ff' }}>{item.scene === 'scene1' ? '场景一' : '场景二'}</span>
                      </div>
                      <button disabled={!item.retriable} onClick={() => retryAlert(item.id)} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #dbe3f0', background: item.retriable ? '#f7fbff' : '#f1f5f9', color: '#1890ff', cursor: item.retriable ? 'pointer' : 'not-allowed' }}>重试</button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          <div className='loginPage'>
            <div className='loginBox'>
              <div className='sliceTitle'><h1>场景切换</h1></div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
                {[{ key: 'scene1', title: '作业指导书 AI 审核', desc: '面向班组作业指导文档' }, { key: 'scene2', title: '高后果区风险管控方案 AI 审核', desc: '面向高后果区风险文档' }].map(s => (
                  <div key={s.key} style={{ border: '1px solid #eef2f7', borderRadius: 12, padding: 14, background: currentScene === s.key ? '#f0f9ff' : '#fff' }}>
                    <div style={{ fontWeight: 700 }}>{s.title}</div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{s.desc}</div>
                    <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                      <button onClick={() => setCurrentScene(s.key)} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #dbe3f0', background: '#fff', color: '#1890ff', cursor: 'pointer' }}>切换至此场景</button>
                      <button onClick={() => setCurrentView('review')} style={{ padding: '8px 12px', borderRadius: 8, border: '1px solid #dbe3f0', background: '#fff', color: '#1f2937', cursor: 'pointer' }}>创建审核任务</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {currentView === 'review' && (
        <>
          {/* 左：文档上传 + 审核（原始主流程） */}
          <div className='background'>
            <div className="uploadContainer">
              <div className="uploadTitle"><h1>上传文档</h1></div>
              <div className='uploadSubtitle'></div>
              <div 
                className={`uploadInputContainer ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <input 
                  type='file' 
                  className='uploadInput' 
                  accept='.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png'
                  onChange={handleFileChange}
                />
                <div className='uploadPlaceholder'>
                  <div className='uploadIcon'>
                    <span className='pdfIcon'>📄</span>
                    <span className='docxIcon'>📝</span>
                  </div>
                  <p>点击或拖拽文件到此处上传</p>
                  <p className='uploadHint'>支持PDF、doc、docx等格式</p>
                </div>
              </div>
              {selectedFilePath && (
                <div className='uploadMeta'>
                  <span className='fileName'>路径：{selectedFilePath}</span>
                  {fileUrl && (
                    <span className='fileLink'> · <a href={fileUrl} target='_blank' rel='noreferrer'>打开本地预览</a></span>
                  )}
                </div>
              )}
              <div className='temperatureContainer'>
                <div className='temperatureLabel'>temperature</div>
                <div className='temperatureSliderContainer'>
                  <input 
                    type='range' 
                    min='0' 
                    max='1' 
                    step='0.01' 
                    value={temperatureValue} 
                    onChange={handleTemperatureChange}
                    className='temperatureSlider' 
                    id='temperatureSlider' 
                  />
                  <div className='temperatureValue'>{temperatureValue}</div>
                </div>
                <div className='temperatureRange'>
                  <span className='rangeMin'>0</span>
                  <span className='rangeMax'>1</span>
                </div>
              </div>
              <div className='reviewButtonContainer'>
                <button className='reviewButton' onClick={handleAnalyze} disabled={!selectedFilePath || submitting}>
                  {submitting ? '分析中...' : '审核文档'}
                </button>
              </div>
            </div>
          </div>
          {/* 右：原文与结果展示 */}
          <div className='loginPage'>
            <div className='loginBox'>
              <div className='sliceTitle'><h1>文档原文</h1></div>
              <div className='sliceSubtitle'></div>
              <div className='sliceInputContainer'>
                <textarea className='sliceInput' placeholder='文档原文将显示在此处' readOnly value={originalContent}></textarea>
              </div>
              <div className='title'><h1>AI审核结果</h1></div>
              <div className='subtitle'></div>
              <div className='resultInputContainer'>
                <textarea className='resultInput' placeholder='AI审核结果将显示在此处' readOnly value={aiResult}></textarea>
              </div>
            </div>
          </div>
        </>
      )}

      

      
    </div>
  );
};

export default Login;