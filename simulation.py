from scene import *

class Frame(SceneObject):
    """
        A 3-dimensional frame scene object.
    """
    def __init__(self, sceneManager, size=[], node=None):
        if len(size) == 0:
            self.size = [1, 1, 1]
        elif len(size) == 1:
            self.size = size[0:1] + [1, 1]
        elif len(size) == 2:
            self.size = size[0:2] + [1]
        elif len(size) == 3:
            self.size = size[0:3]
        SceneObject.__init__(self, sceneManager, node)
    
    def _createMesh(self):
        mesh = self.sceneManager.createManualObject()
        sx, sy, sz = self.size[0], self.size[1], self.size[2]
        n20, n21, n22 = (sx+0.1)*0.5, (sy+0.1)*0.5, (sz+0.1)*0.5
        l0 = [-(0.5*sx+0.05), (0.5*sx+0.05)]
        l1 = [-(0.5*sy+0.05), (0.5*sy+0.05)]
        l2 = [-(0.5*sz+0.05), (0.5*sz+0.05)]
        mb = lambda : mesh.begin('red', ogre.RenderOperation.OT_LINE_STRIP)
        me = lambda : mesh.end()
        po = lambda x, y, z: mesh.position(x, y, z)
        for i in l0:
            for j in l1:
                mb()
                po(i, j, -n22)
                po(i, j, n22)
                me()
        for i in l1:
            for j in l2:
                mb()
                po(-n20, i, j)
                po(n20, i, j)
                me()
        for i in l0:
            for j in l2:
                mb()
                po(i, -n21, j)
                po(i, n21, j)
                me()
        return mesh


from random import random

class ParticlesContainer(SceneObject):
    """
        A particles container.
    """
    def __init__(self, sceneManager, material, count=1, scale=1.0, node=None):
        self.material = material
        SceneObject.__init__(self, sceneManager, node)
        size = [10, 10, 10]
        self.mesh.setDefaultDimensions(scale, scale)
        self.n = count
        self.particles = []
        for i in range(count):
            x = (random()-0.5)*size[0]
            y = (random()-0.5)*size[1]
            z = (random()-0.5)*size[2]
            self.particles.append(self.mesh.createBillboard(Vector3(x,y,z)))
    
    def _createMesh(self):
        bs = self.sceneManager.createBillboardSet()
        bs.setMaterialName(self.material)
        return bs


from time import clock
from subprocess import call
from ctypes import cdll, Structure, c_float, c_uint, c_int, byref

class V3r(Structure):
    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float), ("w", c_float)] # cl_float4

class SimulationScene(Scene):
    """
        The main scene.
    """
    
    def __init__(self, sceneManager, device='gpu', scene_setting='1', magnetic_field=[0,0,0], dt=0.01, kernel_iterations=10, work_group_size=64):
        self.sceneManager = sceneManager
        self.kernel_iterations = kernel_iterations
        self.work_group_size = work_group_size
        self.device = device
        self.frame = Frame(sceneManager, [50,50,4])
        if scene_setting == '1':
            self._scene_setting_1()
        elif scene_setting == '2':
            self._scene_setting_2()
        print 'generating kernel header...'
        with open('kernel.h', 'w') as kernel_header:
            kernel_header.write('#define ln ' + str(work_group_size) + ' // work group size\n')
            kernel_header.write('#define dt ' + str(dt) + ' // iteration delta-time\n')
            kernel_header.write('#define td ' + str(1./dt) + ' // 1/dt\n')
            kernel_header.write('#define dt2 ' + str(dt/2.) + ' // dt/2\n')
            kernel_header.write('static const v3r B=(v3r)(' + str(magnetic_field[0]) + ',' + str(magnetic_field[1]) + ',' + str(magnetic_field[2]) + ',' + str(0) + '); // external magnetic field\n')
        print 'generating host header...'
        with open('host.h', 'w') as kernel_header:
            kernel_header.write('#define ln ' + str(work_group_size) + ' // work group size\n')
            kernel_header.write('#define dt ' + str(dt) + ' // iteration delta-time\n')
            kernel_header.write('#define td ' + str(1./dt) + ' // 1/dt\n')
            kernel_header.write('#define dt2 ' + str(dt/2.) + ' // dt/2\n')
            kernel_header.write('static const v3r B ={{' + str(magnetic_field[0]) + ',' + str(magnetic_field[1]) + ',' + str(magnetic_field[2]) + ',' + str(0) + '}}; // external magnetic field\n')
        if device.lower() == 'cpu':
            print 'building host...'
            if call('make') != 0:
                raise Exception('Error making host')
        self.host = cdll.LoadLibrary('./host.dll')
        print 'initializing OpenCL...'
        self.host.gpu_init(c_uint(self.n), c_uint(work_group_size), byref(self.r_array), byref(self.v_array), byref(self.m_array), byref(self.qe_array), byref(self.qn_array))
    
    def _scene_setting_1(self):
        nn, np, ne = 1000, 1000, 500
        self.nn, self.np, self.ne = nn, np, ne
        
        self.neutron_container = ParticlesContainer(self.sceneManager, 'neutron', nn)
        self.proton_container = ParticlesContainer(self.sceneManager, 'proton', np)
        self.electron_container = ParticlesContainer(self.sceneManager, 'electron', ne)
        
        self.n = n = (nn + np + ne - 1) / self.work_group_size * self.work_group_size + self.work_group_size
        
        V3rArray = V3r*n
        FloatArray = c_float*n
        IntArray = c_int*n
        
        self.m_array = FloatArray(*[0]*n)
        self.qe_array = IntArray(*[0]*n)
        self.qn_array = IntArray(*[0]*n)
        for i in range(nn):
            self.m_array[i] = c_float(939.565)
            self.qn_array[i] = c_int(1)
        for i in range(nn, nn+np):
            self.m_array[i] = c_float(938.272)
            self.qe_array[i] = c_int(1)
            self.qn_array[i] = c_int(1)
        for i in range(nn+np, nn+np+ne):
            self.m_array[i] = c_float(0.511)
            self.qe_array[i] = c_int(-1)
        
        self.r_array = V3rArray(*[V3r(0,0,0)]*n)
        size = [100, 100, 10]
        for i in range(n):
            x = (random()-0.5)*size[0]
            y = (random()-0.5)*size[1]
            z = (random()-0.5)*size[2]
            self.r_array[i] = V3r(x,y,z)
        
        self.v_array = V3rArray(*[V3r(0,0,0)]*n)
        #for i in range(n):
        #    self.v_array[i] = V3r(self.r_array[i].y*0.01, -self.r_array[i].x*0.01, 0)
        
        self._set_positions()

    def _scene_setting_2(self):
        nn, np, ne = 1000, 1000, 1000
        self.nn, self.np, self.ne = nn, np, ne
        
        self.neutron_container = ParticlesContainer(self.sceneManager, 'neutron', nn)
        self.proton_container = ParticlesContainer(self.sceneManager, 'proton', np)
        self.electron_container = ParticlesContainer(self.sceneManager, 'electron', ne)
        
        self.n = n = (nn + np + ne - 1) / self.work_group_size * self.work_group_size + self.work_group_size
        
        V3rArray = V3r*n
        FloatArray = c_float*n
        IntArray = c_int*n
        
        self.m_array = FloatArray(*[0]*n)
        self.qe_array = IntArray(*[0]*n)
        self.qn_array = IntArray(*[0]*n)
        for i in range(nn):
            self.m_array[i] = c_float(939.565)
            self.qn_array[i] = c_int(1)
        for i in range(nn, nn+np):
            self.m_array[i] = c_float(938.272)
            self.qe_array[i] = c_int(1)
            self.qn_array[i] = c_int(1)
        for i in range(nn+np, nn+np+ne):
            self.m_array[i] = c_float(0.511)
            self.qe_array[i] = c_int(-1)
        
        self.r_array = V3rArray(*[V3r(0,0,0)]*n)
        size = [40, 20, 20]
        for i in range(nn):
            x = (random()-0.5)*size[0] - 60
            y = (random()-0.5)*size[1]
            z = (random()-0.5)*size[2]
            self.r_array[i] = V3r(x,y,z)
        for i in range(nn, n):
            x = (random()-0.5)*size[0] + 60
            y = (random()-0.5)*size[1]
            z = (random()-0.5)*size[2]
            self.r_array[i] = V3r(x,y,z)
        
        self.v_array = V3rArray(*[V3r(0,0,0)]*n)
        for i in range(nn):
            self.v_array[i] = V3r(1, 0, 0)
        for i in range(nn, n):
            self.v_array[i] = V3r(-1, 0, 0)
        
        self._set_positions()
    
    def _set_positions(self):
        for i in range(self.nn):
            r = self.r_array[i]
            self.neutron_container.particles[i].setPosition(r.x,r.y,r.z)
        for i in range(self.np):
            r = self.r_array[i+self.nn]
            self.proton_container.particles[i].setPosition(r.x,r.y,r.z)
        for i in range(self.ne):
            r = self.r_array[i+self.nn+self.np]
            self.electron_container.particles[i].setPosition(r.x,r.y,r.z)
    
    def reinit(self):
        pass
    
    def update(self, dt):
        if self.device.lower() == 'gpu':
            self.update_gpu()
        else:
            self.update_cpu()
    
    def update_gpu(self):
        #t0 = clock()
        for i in range(self.kernel_iterations):
            self.host.gpu_update()
        self.host.gpu_getval(byref(self.r_array))
        #t1 = clock()
        self._set_positions()
        #t2 = clock()
        #print t1-t0, t2-t1
    
    def update_cpu(self):
        n = self.n
        #t0 = clock()
        for i in range(self.kernel_iterations):
           self. host.cpu_update(c_uint(n), byref(self.r_array), byref(self.v_array), byref(self.m_array), byref(self.qe_array), byref(self.qn_array))
        #t1 = clock()
        self._set_positions()
        #t2 = clock()
        #print t1-t0, t2-t1
