import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  User,
  Briefcase,
  Plus,
  ExternalLink,
  Image as ImageIcon,
  Video,
  FileText,
  Link as LinkIcon,
  Edit,
  Trash2,
  Save
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CreatorPortfolio = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    display_name: '',
    bio: '',
    skills: [],
    social_links: {}
  });
  const [newSkill, setNewSkill] = useState('');
  const [showAddItem, setShowAddItem] = useState(false);
  const [newItem, setNewItem] = useState({
    title: '',
    description: '',
    type: 'project',
    external_link: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/creator/profile`);
      const data = await response.json();
      setProfile(data);
      setFormData({
        display_name: data.display_name || '',
        bio: data.bio || '',
        skills: data.skills || [],
        social_links: data.social_links || {}
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      const method = profile && profile.display_name ? 'PUT' : 'POST';
      const response = await fetch(`${API_URL}/api/creator/profile`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.success) {
        setProfile(data.profile);
        setEditMode(false);
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
    }
  };

  const handleAddSkill = () => {
    if (newSkill.trim() && !formData.skills.includes(newSkill.trim())) {
      setFormData({
        ...formData,
        skills: [...formData.skills, newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skill) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter(s => s !== skill)
    });
  };

  const handleAddPortfolioItem = async () => {
    try {
      const response = await fetch(`${API_URL}/api/creator/portfolio/item`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newItem)
      });
      const data = await response.json();
      if (data.success) {
        await loadProfile();
        setShowAddItem(false);
        setNewItem({ title: '', description: '', type: 'project', external_link: '' });
      }
    } catch (error) {
      console.error('Failed to add portfolio item:', error);
    }
  };

  const handleDeleteItem = async (itemId) => {
    try {
      const response = await fetch(`${API_URL}/api/creator/portfolio/item/${itemId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        await loadProfile();
      }
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const getItemIcon = (type) => {
    switch (type) {
      case 'image': return <ImageIcon className="w-5 h-5" />;
      case 'video': return <Video className="w-5 h-5" />;
      case 'link': return <LinkIcon className="w-5 h-5" />;
      case 'document': return <FileText className="w-5 h-5" />;
      default: return <Briefcase className="w-5 h-5" />;
    }
  };

  if (loading && !profile) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading portfolio...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Creator Portfolio</h2>
          <p className="text-gray-600 mt-2">Showcase your work and expertise</p>
        </div>
        <Button
          onClick={() => editMode ? handleSaveProfile() : setEditMode(true)}
          variant={editMode ? 'default' : 'outline'}
        >
          {editMode ? (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </>
          ) : (
            <>
              <Edit className="w-4 h-4 mr-2" />
              Edit Profile
            </>
          )}
        </Button>
      </div>

      {/* Profile Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Profile Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          {editMode ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Display Name</label>
                <Input
                  value={formData.display_name}
                  onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Bio</label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  placeholder="Tell us about yourself..."
                  className="w-full border rounded-md p-3 min-h-[100px]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Skills</label>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                    placeholder="Add a skill..."
                  />
                  <Button onClick={handleAddSkill}>Add</Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.skills.map((skill) => (
                    <Badge key={skill} variant="secondary" className="cursor-pointer hover:bg-red-100">
                      {skill}
                      <button
                        onClick={() => handleRemoveSkill(skill)}
                        className="ml-2 text-red-600"
                      >
                        ×
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="text-2xl font-bold">{profile?.display_name || 'Your Name'}</h3>
                <p className="text-gray-600 mt-2">{profile?.bio || 'No bio yet'}</p>
              </div>
              {profile?.skills && profile.skills.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-gray-600 mb-2">Skills</p>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.map((skill) => (
                      <Badge key={skill} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Portfolio Items */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Portfolio
              </CardTitle>
              <CardDescription>Showcase your best work</CardDescription>
            </div>
            <Button onClick={() => setShowAddItem(!showAddItem)} size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Add Item
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Add Item Form */}
          {showAddItem && (
            <Card className="mb-4 bg-blue-50 border-blue-200">
              <CardContent className="pt-6">
                <div className="space-y-3">
                  <Input
                    placeholder="Title"
                    value={newItem.title}
                    onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                  />
                  <textarea
                    placeholder="Description"
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                    className="w-full border rounded-md p-3 min-h-[80px]"
                  />
                  <div className="flex gap-3">
                    <select
                      value={newItem.type}
                      onChange={(e) => setNewItem({ ...newItem, type: e.target.value })}
                      className="border rounded-md px-3 py-2 flex-1"
                    >
                      <option value="project">Project</option>
                      <option value="image">Image</option>
                      <option value="video">Video</option>
                      <option value="link">Link</option>
                      <option value="document">Document</option>
                    </select>
                    <Input
                      placeholder="External link (optional)"
                      value={newItem.external_link}
                      onChange={(e) => setNewItem({ ...newItem, external_link: e.target.value })}
                      className="flex-1"
                    />
                  </div>
                  <div className="flex gap-2 justify-end">
                    <Button variant="outline" onClick={() => setShowAddItem(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddPortfolioItem}>
                      Add to Portfolio
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Portfolio Items Grid */}
          {profile?.portfolio_items && profile.portfolio_items.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.portfolio_items.map((item) => (
                <Card key={item.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                          {getItemIcon(item.type)}
                        </div>
                        <div>
                          <h4 className="font-semibold">{item.title}</h4>
                          <Badge variant="outline" className="text-xs mt-1">
                            {item.type}
                          </Badge>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteItem(item.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{item.description}</p>
                    {item.external_link && (
                      <a
                        href={item.external_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
                      >
                        View Project <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Briefcase className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No portfolio items yet</p>
              <p className="text-sm mt-1">Click "Add Item" to showcase your work</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CreatorPortfolio;
