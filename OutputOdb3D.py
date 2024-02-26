# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import visualization
import displayGroupOdbToolset as dgo


def out_acc_data(odb, step, nodelist, fpath):
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('A', 
        NODAL, ((COMPONENT, 'A1'), (COMPONENT, 'A2'), (COMPONENT, 'A3'), )), ), nodeLabels=(('PART-1-1', (
        nodelist[0], nodelist[1], nodelist[2], )), ))
    x0 = session.xyDataObjects['A:A1 PI: PART-1-1 N: ' + nodelist[0]]
    x1 = session.xyDataObjects['A:A1 PI: PART-1-1 N: ' + nodelist[1]]
    x2 = session.xyDataObjects['A:A1 PI: PART-1-1 N: ' + nodelist[2]]
    x3 = session.xyDataObjects['A:A2 PI: PART-1-1 N: ' + nodelist[0]]
    x4 = session.xyDataObjects['A:A2 PI: PART-1-1 N: ' + nodelist[1]]
    x5 = session.xyDataObjects['A:A2 PI: PART-1-1 N: ' + nodelist[2]]
    x6 = session.xyDataObjects['A:A3 PI: PART-1-1 N: ' + nodelist[0]]
    x7 = session.xyDataObjects['A:A3 PI: PART-1-1 N: ' + nodelist[1]]
    x8 = session.xyDataObjects['A:A3 PI: PART-1-1 N: ' + nodelist[2]]
    session.writeXYReport(fileName=fpath + '.out', appendMode=OFF, xyData=(x0, x1, 
        x2, x3, x4, x5, x6, x7, x8))


def output_disp_data_last_frame(odb, group, group_type, step, fpath):
    """导出最后一帧位移数据
    """
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    step_id = odb.steps.keys().index(step)
    num_frames = len(odb.steps[step].frames) - 1
    session.writeFieldReport(fileName=fpath + '.csv', append=OFF, 
        sortItem='结点编号', odb=odb, step=step_id, frame=num_frames, outputPosition=NODAL, 
        variable=(('U', NODAL, ((COMPONENT, 'U1'), (COMPONENT, 'U2'), (COMPONENT, 'U3'), )), ))
    

def output_disp_data_all_frame(odb, group, group_type, step, fpath):
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)    
    step_id = odb.steps.keys().index(step)
    
    for i in range(len(odb.steps[step].frames)):
        session.writeFieldReport(fileName=fpath + '.csv', append=ON, 
            sortItem='结点编号', odb=odb, step=step_id, frame=i, outputPosition=NODAL, 
            variable=(('U', NODAL, ((COMPONENT, 'U1'), (COMPONENT, 'U2'), (COMPONENT, 'U3'), )), ))
    

def output_stre_data_last_frame(odb, group, group_type, step, fpath):
    """导出最后一帧应力数据
    """
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    step_id = odb.steps.keys().index(step)
    num_frames = len(odb.steps[step].frames) - 1
    session.writeFieldReport(fileName=fpath + '.csv', append=OFF, 
        sortItem='结点编号', odb=odb, step=step_id, frame=num_frames, outputPosition=NODAL, 
        variable=(('S', INTEGRATION_POINT, ((INVARIANT, 
        'Max. Principal'), (INVARIANT, 'Min. Principal'), )), ))
    

def output_stre_data_env(odb, group, group_type, step, fpath):
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    
    #: ---- Creating Field Output From Frames ----
    odbname = session.viewports['Viewport: 1'].odbDisplay.name
    step_frames = session.odbs[odbname].steps[step].frames
    all_frames = []
    for i in range(len(step_frames)):
        all_frames.append(step_frames[i].fieldOutputs['S'])           
    (maxField_S, maxIndex_S) = visualization.maxEnvelope(all_frames, MAX_PRINCIPAL)
    (minField_S, minIndex_S) = visualization.minEnvelope(all_frames, MIN_PRINCIPAL)
    
    currentOdb = session.odbs[odbname]
    scratchOdb = session.ScratchOdb(odb=currentOdb)
    sessionStep = scratchOdb.Step(name='Session Step', 
    description='Step for Viewer non-persistent fields', 
    domain=TIME, timePeriod=1.0)
    reservedFrame = sessionStep.Frame(frameId=0, frameValue=0.0, 
        description='Session Frame')
        
    sessionFrame_max = sessionStep.Frame(frameId=1, frameValue=0.0, 
    description='The maximum value over all selected frames')
    sessionField_max = sessionFrame_max.FieldOutput(name='S_max', 
    description='Stress components (maximum envelope) using Max. Principal',
        field=maxField_S)
    sessionField_max = sessionFrame_max.FieldOutput(name='S_max_Index', 
    description='Indices into list of S fields selected for maximum envelope', 
        field=maxIndex_S) 

    sessionFrame_min = sessionStep.Frame(frameId=2, frameValue=0.0, 
    description='The minimum value over all selected frames')
    sessionField_min = sessionFrame_min.FieldOutput(name='S_min', 
    description='Stress components (minimum envelope) using Min. Principal',
        field=minField_S)
    sessionField_min = sessionFrame_min.FieldOutput(name='S_min_Index', 
    description='Indices into list of S fields selected for minimum envelope', 
        field=minIndex_S)
    #: ---- End of Creating Field Output From Frames ----
     
    frame1 = session.scratchOdbs[odbname].steps['Session Step'].frames[1]
    session.viewports['Viewport: 1'].odbDisplay.setFrame(frame=frame1)
    odb = session.scratchOdbs[odbname]
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    session.writeFieldReport(fileName=fpath + '-max.csv', append=OFF, sortItem='结点编号', 
        odb=odb, step=0, frame=1, outputPosition=NODAL, variable=(('S_max', 
        INTEGRATION_POINT, ((INVARIANT, 'Max. Principal'), )), ))
        
    frame2 = session.scratchOdbs[odbname].steps['Session Step'].frames[2]
    session.viewports['Viewport: 1'].odbDisplay.setFrame(frame=frame2)
    odb = session.scratchOdbs[odbname]
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    session.writeFieldReport(fileName=fpath + '-min.csv', append=OFF, sortItem='结点编号', 
        odb=odb, step=0, frame=2, outputPosition=NODAL, variable=(('S_min', 
        INTEGRATION_POINT, ((INVARIANT, 'Min. Principal'), )), ))
    

def output_slide_data_last_frame(odb, group, group_type, step, fpath):
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    step_id = odb.steps.keys().index(step)
    num_frames = len(odb.steps[step].frames) - 1
    session.writeFieldReport(fileName=fpath + '.csv', append=OFF, 
        sortItem='结点编号', odb=odb, step=step_id, frame=num_frames, outputPosition=NODAL, 
        variable=(('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), (COMPONENT, 'S22'), (COMPONENT, 'S33'), (COMPONENT, 'S12'), (COMPONENT, 'S13'), (COMPONENT, 'S23'), )), ))
    

def output_slide_data_all_frame(odb, group, group_type, step, fpath):
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    step_id = odb.steps.keys().index(step)
    for i in range(len(odb.steps[step].frames)):
        session.writeFieldReport(fileName=fpath + '.csv', append=ON, 
            sortItem='结点编号', odb=odb, step=step_id, frame=i, outputPosition=NODAL, 
            variable=(('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), (COMPONENT, 'S22'), (COMPONENT, 'S33'), (COMPONENT, 'S12'), (COMPONENT, 'S13'), (COMPONENT, 'S23'), )), ))
        

def out_dmgt_data(odb, group, group_type, step, frames, fpath):
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)   
    if group_type == 'Nset':
        leaf = dgo.LeafFromNodeSets(nodeSets=('PART-1-1.%s' % group, ))
    elif group_type == 'Elset':
        leaf = dgo.LeafFromElementSets(elementSets=('PART-1-1.%s' % group, ))
    else:
        leaf = dgo.LeafFromSurfaceSets(surfaceSets=(group, ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    step_id = odb.steps.keys().index(step)
    for frame in frames:
        if frame != -1:   
            session.writeFieldReport(fileName=fpath + '_' + str(frame) + '.csv', append=OFF, 
                sortItem='结点编号', odb=odb, step=step_id, frame=frame, 
                outputPosition=NODAL, variable=(('DAMAGET', INTEGRATION_POINT), 
                ))
        else:
            num_frames = len(odb.steps[step].frames) - 1
            session.writeFieldReport(fileName=fpath + '_' + str(frame) + '.csv', append=OFF, 
                sortItem='结点编号', odb=odb, step=step_id, frame=num_frames, 
                outputPosition=NODAL, variable=(('DAMAGET', INTEGRATION_POINT), 
                ))